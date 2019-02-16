from __future__ import division

import rospy
import numpy as np

from pybuilt.controls.abstract_effector_server import AbstractEffectorServer
from pybuilt.controls.vehicles.d6.kinematics import d6_blade_kinematics
from pybuilt.controls.vehicles.d6.joysticks import JsBladeHeightPublisher, JsBladeRollPublisher, JsBladeYawPublisher
from pybuilt.controls.algorithms.fpid import PIController
from pybuilt.controls.util.expected_velocity_helper import ExpectedVelocityHelper
from pybuilt.controls.algorithms.position_controller import PPositionController
from pybuilt.hardware.drivers.gamepad import Gamepad
from pybuilt.util.action.action_helpers import UPDATE_IN_PLACE_ON_MAIN_THREAD

from pybuilt.util.action.action_state import BuiltActionState
from pybuilt.util.action.action_helpers import READY_STATE_NAME
from pybuilt.util.timing.rate import Rate
from pybuilt.util.helpers import init_blogger
from pybuilt.util.timing.timer import Timer

from built.msg import VpatGoal, VpatResult, EngineStatistics

CALIBRATE_YAW_STATE = 'calibrate_yaw'
DETERMINE_STATE = 'determine_state'
COMMAND_POSITION_STATE = 'command_position'


class VpatServer(AbstractEffectorServer):
    """A State Machine responsible for handling all goals related to the blade which includes controlling:

    - Blade height
    - Blade roll
    - Blade yaw

    Blade height and yaw can't be changed at the same time.
    """

    def __init__(self, imu_rate_hz):
        super(VpatServer, self).__init__(VpatGoal, VpatResult, namespace_prefix='~vpat/')

        self._initialize_constants()
        self.yaw_calibrated = False
        self.state_after_yaw = None
        self.rate_hz = self.param('vpat_server/rate_hz')

        self.kinematics = d6_blade_kinematics.D6BladeKinematics(imu_rate_hz)

        # Message publishers to control blade height, roll, and yaw
        self.blade_height_pub = JsBladeHeightPublisher()
        self.blade_roll_pub = JsBladeRollPublisher()
        self.blade_yaw_pub = JsBladeYawPublisher()

        # Controller setup and status tracking
        self._setup_height_controller()
        self._setup_roll_controller()
        self._setup_yaw_controller()

        # Check for override
        self.gamepad = Gamepad()

        self.goal_timeout = Timer(0, periodic=False)

        self.engine_rpm = self.gparam('machine_hw/max_rpm')

        self.add_states(
            BuiltActionState(READY_STATE_NAME, next_states=DETERMINE_STATE),
            BuiltActionState(
                DETERMINE_STATE,
                func=self._determine_state,
                next_states=[CALIBRATE_YAW_STATE, COMMAND_POSITION_STATE, READY_STATE_NAME]),
            BuiltActionState(
                CALIBRATE_YAW_STATE,
                func=self._calibrate_yaw,
                next_states=[CALIBRATE_YAW_STATE, COMMAND_POSITION_STATE, READY_STATE_NAME]),
            BuiltActionState(COMMAND_POSITION_STATE, func=self._command_position, next_states=[READY_STATE_NAME]))

        rospy.Subscriber('machine_hw/engine_statistics', EngineStatistics, self._receive_rpm, queue_size=1)

    # --------------------------------------------
    # State methods
    # --------------------------------------------

    def verify_goal_params(self, goal):
        """Check our goal is mechanically possible for this blade.

        :param goal:
        :return:
        """
        # This cross slope roll != blade roll, but it's close enough for now
        roll_in_bounds = self.min_roll <= goal.cross_slope_angle_degs <= self.max_roll
        yaw_in_bounds = self.min_yaw <= goal.yaw_angle_degs <= self.max_yaw
        height_in_bounds = self.min_height <= goal.center_blade_height <= self.max_height

        accepted = roll_in_bounds and yaw_in_bounds and height_in_bounds
        reason = None
        if not accepted:
            reason = ''
            reason += 'roll outside bounds <req: {:2.2f}>. '.format(
                goal.cross_slope_angle_degs) if not roll_in_bounds else ''
            reason += 'yaw outside bounds <req: {:2.2f}>. '.format(goal.yaw_angle_degs) if not yaw_in_bounds else ''
            reason += 'height outside bounds <req: {:2.2f}>.'.format(
                goal.center_blade_height) if not height_in_bounds else ''
            log.e('Goal not accepted because {}'.format(reason))

        return accepted, reason

    def which_update_type_accepted(self, current_goal, update_goal):
        """Update goal after next sleep."""
        return UPDATE_IN_PLACE_ON_MAIN_THREAD

    def update_goal(self, current_goal, update_type, goal_update):
        """Updates all the goal parameters.

        :param current_goal:
        :param update_type:
        :param goal_update:
        :return:
        """
        current_goal.goal_type = goal_update.goal_type

        current_goal.accuracy = goal_update.accuracy

        current_goal.maintain = goal_update.maintain

        current_goal.cross_slope_angle_degs = goal_update.cross_slope_angle_degs
        current_goal.yaw_angle_degs = goal_update.yaw_angle_degs
        current_goal.center_blade_height = goal_update.center_blade_height
        current_goal.timeout = goal_update.timeout

        self._init_controllers_from_goal(current_goal, current_goal.accuracy)

    def fill_result_msg(self, result_msg, goal):
        blade_xyz, cross_slope, joint_angles = self._get_blade_info()
        result_msg.cross_slope_angle_degs = cross_slope
        result_msg.yaw_angle_degs = joint_angles['yaw']
        result_msg.center_blade_height = blade_xyz[2]

    def _determine_state(self):
        """Look at the goal_type and transition to another state.

        If yaw hasn't been calibrated yet, run the yaw calibration before transitioning to another state.
        """
        if self.goal.goal_type == VpatGoal.GOAL_TYPE_COMMAND_POSITION_NO_YAW:
            next_state_name = COMMAND_POSITION_STATE
        else:
            next_state_name = next((x.name for x in self.states if x.name == self.goal.goal_type), None)

        if not next_state_name:
            self.finish_failure('Invalid state {}'.format(next_state_name))

        # Calibrate yaw first then move to another state
        self.request_transition(next_state_name) # skips yaw calibration! -- DON"T MERGE!
        if not self._is_yaw_expired() and self.yaw_calibrated and next_state_name != VpatGoal.GOAL_TYPE_CALIBRATE_YAW:
            self.request_transition(next_state_name)
        else:
            log.w('Calibrating yaw before moving to state {}'.format(next_state_name))
            self.state_after_yaw = next_state_name
            self.request_transition(CALIBRATE_YAW_STATE)

    def _command_position(self):
        """Command positions relative to the vehicle frame. Think of the controls 'attached' to the vehicle.

        For instance if the blade height is set to some height above the ground and the vehicle pitches,
        the blade will also pitch forward.

        This state is mainly used to set the blade to some position in the 'vehicle' frame.
        This can be used to some some heavy bulldozing.

        If the yaw != the current yaw, the blade will be yawed first before reaching the right height and
        cross slope. Then the blade will go to the desired cross-slope and height.

        NOTE: you should try to avoid changing the yaw angle while moving because of the problems explained
        in the calibrate yaw state.

        TODO:
        - Check limit of joints and see if the yaw or roll joint is stuck and fail if it's stuck.
        """
        self._init_controllers_from_goal(self.goal, self.goal.accuracy)

        rate = Rate(self.rate_hz, 'vpat')
        while True:
            blade_xyz, cross_slope, joint_angles = self._get_blade_info()
            if self.goal.goal_type == VpatGoal.GOAL_TYPE_COMMAND_POSITION_NO_YAW:
                yaw_reached = True
            else:
                yaw_reached = self._control_yaw(joint_angles['yaw'])

            # Wait until yaw position is reached until doing the height and roll control
            if yaw_reached:
                height_reached = self._control_vpat_height(blade_xyz[2])
                roll_reached = self._control_cross_slope_roll(cross_slope)
                if yaw_reached and height_reached and roll_reached and not self.goal.maintain:
                    log.d('Success. height {:2.2f} yaw {:2.2f} roll {:2.2f}'.format(blade_xyz[2], joint_angles['yaw'],
                                                                                    cross_slope))
                    self.finish_success()

            self._check_failure_conditions()
            self.sleep_and_yield_rate(rate)

    def _calibrate_yaw(self):
        """Calibrate or re-calibrate the yaw angle of the blade, since it's unknown on startup and can drift overtime.

        Raises the blade up, yaws the blade to the reset position, and resets the yaw angle counter.

        NOTE: The vehicle should NOT be not moving when the yaw is being calibrated. This doesn't currently
        get the blade yaw relative to the vehicle - if the vehicle is yawing when the blade is yawing,
        the final integration will include both yaws.
        """
        log.i('Starting yaw calibration action')
        self.height_controller.set_goal(self.yaw_reset_arm_height)
        self.height_controller.set_error_bound(self.yaw_reset_height_error)

        curr_yaw_angle = self.kinematics.get_yaw_angle_degs()
        blade_yaw_timer = Timer(self.param('vpat_server/calibrate_yaw/yaw_movement_expire_time'))
        rate = Rate(self.rate_hz, 'vpat')
        while True:
            curr_xyz, _, joint_angles = self._get_blade_info()

            # Start yawing the blade once the arm height is at or above some height
            if curr_xyz[2] >= self.yaw_reset_arm_height or self._control_vpat_height(curr_xyz[2]):
                if not blade_yaw_timer.running():
                    blade_yaw_timer.start()

                self.blade_yaw_pub.publish_deflection(self.yaw_deflection)

                if self.gamepad.is_override_active():
                    log.w('Override held during calibration, resetting calibration timer', throttle=1.0)
                    blade_yaw_timer.reset()
                    blade_yaw_timer.start()

                if not np.isclose(joint_angles['yaw'], curr_yaw_angle, rtol=0):
                    blade_yaw_timer.reset()
                    blade_yaw_timer.start()

                    # Re-run yaw calibration if it's going the wrong way for some weird reason.
                    if not self.gamepad.is_override_active() and joint_angles['yaw'] < curr_yaw_angle:
                        fail_msg = 'Yaw calibration going the wrong way!!!! curr={} prev={}'.format(
                            joint_angles['yaw'], curr_yaw_angle)
                        log.f(fail_msg)
                        self.request_transition(CALIBRATE_YAW_STATE)

                    curr_yaw_angle = joint_angles['yaw']

                # Once blade movement hasn't been sensed for some time, the yaw can be considered to be at the hard stop
                if blade_yaw_timer.is_ready():
                    break

            self.sleep_and_yield_rate(rate)

        log.i('Done calibrating yaw.')
        self.kinematics.reset_yaw_angle_degs(self.max_yaw)
        self.yaw_calibrated = True

        if self.state_after_yaw and self.state_after_yaw != CALIBRATE_YAW_STATE:
            self.request_transition(self.state_after_yaw)
        else:
            self.finish_success()

    # --------------------------------------------
    # Control methods for yaw, height, and roll of vpat blade
    # --------------------------------------------

    def _control_yaw(self, curr_yaw_angle):
        """Updates the yaw controller.

        :param curr_yaw_angle:
        :return: True if it's reached it's goal
        """
        self.yaw_controller.set_state(curr_yaw_angle)
        yaw_reached = self.yaw_controller.is_goal_reached()

        # Dynamically set debug from parameter server
        self.yaw_controller.set_debug(self.param('yaw_controller/debug'))

        if not yaw_reached:
            self.blade_yaw_pub.publish_deflection(
                self.yaw_controller.get_control_effort(
                    self.gamepad.is_override_active(), engine_rpm_scale=self._calc_engine_rpm_scale()))
        else:
            self.blade_yaw_pub.publish_deflection(0)

        return yaw_reached

    def _control_vpat_height(self, curr_height):
        """Updates the height controller.

        :param curr_height:
        :return:
        """
        self.height_controller.set_state(curr_height)
        height_reached = self.height_controller.is_goal_reached()

        # Dynamically set debug from parameter server
        self.height_controller.set_debug(self.param('height_controller/debug'))

        if not height_reached:
            self.blade_height_pub.publish_deflection(
                self.height_controller.get_control_effort(
                    self.gamepad.is_override_active(), engine_rpm_scale=self._calc_engine_rpm_scale()))
        else:
            self.blade_height_pub.publish_deflection(0)
        return height_reached

    def _control_cross_slope_roll(self, curr_cross_slope):
        """Update the roll controller.

        :param curr_cross_slope: Current cross slope roll of the blade
        :return:
        """
        self.roll_controller.set_state(curr_cross_slope)
        roll_reached = self.roll_controller.is_goal_reached()

        # Dynamically set debug from parameter server
        self.roll_controller.set_debug(self.param('roll_controller/debug'))

        if not roll_reached:
            self.blade_roll_pub.publish_deflection(
                self.roll_controller.get_control_effort(
                    self.gamepad.is_override_active(), engine_rpm_scale=self._calc_engine_rpm_scale()))
        else:
            self.blade_roll_pub.publish_deflection(0)
        return roll_reached

    # --------------------------------------------
    # Helpers
    # --------------------------------------------

    def _check_failure_conditions(self):
        # Check for failure conditions
        if self._is_yaw_expired():
            self.yaw_calibrated = False
            self.finish_failure('Yaw expired. Recalibrate yaw', fail_type=VpatResult.FAIL_TYPE_YAW_EXPIRED)
        elif self.goal_timeout.is_ready(autostart=False) and not self.goal.maintain:
            self.finish_failure('Failed to reach position in {}s. <'.format(self.goal_timeout.duration))

    def _get_blade_info(self):
        """Returns the current z-height of the bottom edge of the blade.

        :return blade xyz position relative to base link and cross slope roll
        """
        curr_kinematics = self.kinematics.get_kinematic_information()
        blade_xyz = curr_kinematics[d6_blade_kinematics.END_EFFECTOR_BASE_LINK_KEY]
        joint_angles = curr_kinematics[d6_blade_kinematics.JOINT_ANGLES_KEY]
        cross_slope = curr_kinematics[d6_blade_kinematics.CROSS_SLOPE_KEY]
        return blade_xyz, cross_slope, joint_angles

    def _is_yaw_expired(self):
        """Returns True if yaw angle has expired or marked as uncalibrated."""
        return self.kinematics.get_total_yaw_time() >= self.param('vpat_server/yaw_expiration_time')

    def reset_state(self):
        """Resets the state machine to prepare for the next state."""
        self.blade_height_pub.reset()
        self.blade_yaw_pub.reset()
        self.blade_roll_pub.reset()

        self.kinematics.reset()

        self.height_controller.reset()
        self.roll_controller.reset()
        self.yaw_controller.reset()

        self.state_after_yaw = None
        self.static_check_state = None

        self.goal_timeout.reset()

    def _is_stuck(self, maintain=False, scale=1.0):
        """Determine if the blade is stuck or not.

        TODO: We should determine if we've yawed too far for the cross slope we want.
        """
        return False

    def _is_static(self):
        """Determine if the blade is static.

        TODO: check to see if arm joint angles haven't changed more than 1-2 degrees in the past few seconds
        :return:
        """
        return False

    def update_imu(self, cab_imu_data, arm_imu_data, blade_imu_data):
        """Updates the D6 kinematics with the newest cab and blade imu readings.

        :param cab_imu_data: list of new cab imu data
        :param arm_imu_data: list of new arm imu data
        :param blade_imu_data: list of new blade imu data
        """
        self.kinematics.update(cab_imu_data, arm_imu_data, blade_imu_data)

    def update_control_status(self, ts, blade_height_deflection, blade_roll_deflection, blade_yaw_deflection):
        """Updates the control status of things being driven. This is needed so we can know when to do yaw integration.

        Majority of the time, the dozer server will know what control is being
        sent, but during override we want to integrate yaw, which it may not
        know about.

        :param ts: timestamp when the message was created
        :param blade_height_deflection: blade height deflection
        :param blade_roll_deflection: blade roll deflection
        :param blade_yaw_deflection: blade yaw deflection
        """
        self.kinematics.update_control_status(ts, blade_height_deflection, blade_roll_deflection, blade_yaw_deflection)

    # -------------------------------------------------------------
    # Initialization Helper Methods
    # -------------------------------------------------------------

    def _init_controllers_from_goal(self, goal, accuracy):
        """Initialize height, roll and yaw controllers from a goal."""
        self.height_controller.set_goal(goal.center_blade_height)
        self.roll_controller.set_goal(goal.cross_slope_angle_degs)
        if goal.goal_type != VpatGoal.GOAL_TYPE_COMMAND_POSITION_NO_YAW:
            self.yaw_controller.set_goal(goal.yaw_angle_degs)

        if accuracy == VpatGoal.ACCURACY_NEVER_SATISFIED:
            height_err = self.param('vpat_server/never_satisfied_accuracy/height_err')
            cross_slope_err = self.param('vpat_server/never_satisfied_accuracy/roll_err')
            yaw_err = self.param('vpat_server/never_satisfied_accuracy/yaw_err')
        elif accuracy == VpatGoal.ACCURACY_FINER:
            height_err = self.param('vpat_server/finer_accuracy/height_err')
            cross_slope_err = self.param('vpat_server/finer_accuracy/roll_err')
            yaw_err = self.param('vpat_server/finer_accuracy/yaw_err')
        elif accuracy == VpatGoal.ACCURACY_FINEST:
            height_err = self.param('vpat_server/finest_accuracy/height_err')
            cross_slope_err = self.param('vpat_server/finest_accuracy/roll_err')
            yaw_err = self.param('vpat_server/finest_accuracy/yaw_err')
        else:  # assume rough accuracy
            height_err = self.param('vpat_server/rough_accuracy/height_err')
            cross_slope_err = self.param('vpat_server/rough_accuracy/roll_err')
            yaw_err = self.param('vpat_server/rough_accuracy/yaw_err')

        self.roll_controller.set_error_bound(cross_slope_err)
        self.height_controller.set_error_bound(height_err)
        self.yaw_controller.set_error_bound(yaw_err)

        self.goal_timeout.reset(duration=goal.timeout, periodic=False)
        self.goal_timeout.start()

    def _setup_height_controller(self):
        """Initializes the height controller and expected velocities."""
        self.height_controller_config = self.param('height_controller')
        fpid_controller = PIController(
            k_p=self.height_controller_config['kp_velocity'],
            k_i=self.height_controller_config['ki_velocity'],
            k_f=self.height_controller_config['kf_velocity'],
            pos_limit=self.height_controller_config['pos_limit'],
            neg_limit=self.height_controller_config['neg_limit'],
            rate=self.rate_hz,
            sat_limit=self.height_controller_config['sat_limit'])
        self.height_controller = PPositionController(
            kp=self.height_controller_config['kp_position'],
            velocity_controller=fpid_controller,
            controller_rate=self.rate_hz,
            inverted_controls=self.height_controller_config['inverted_controls'],
            min_control_effort=self.height_controller_config['min_control'],
            name='height')
        expected_velocities_helper = ExpectedVelocityHelper(self.height_controller_config['expected_velocities_file'])
        self.height_controller.set_expected_velocity_helper(expected_velocities_helper)

    def _setup_roll_controller(self):
        """Initializes the roll controller and expected velocities."""
        self.roll_controller_config = self.param('roll_controller')
        fpid_controller = PIController(
            k_p=self.roll_controller_config['kp_velocity'],
            k_i=self.roll_controller_config['ki_velocity'],
            k_f=self.roll_controller_config['kf_velocity'],
            pos_limit=self.roll_controller_config['pos_limit'],
            neg_limit=self.roll_controller_config['neg_limit'],
            rate=self.rate_hz,
            sat_limit=self.roll_controller_config['sat_limit'])
        self.roll_controller = PPositionController(
            kp=self.roll_controller_config['kp_position'],
            velocity_controller=fpid_controller,
            controller_rate=self.rate_hz,
            inverted_controls=self.roll_controller_config['inverted_controls'],
            min_control_effort=self.roll_controller_config['min_control'],
            name='roll')
        expected_velocities_helper = ExpectedVelocityHelper(self.roll_controller_config['expected_velocities_file'])
        self.roll_controller.set_expected_velocity_helper(expected_velocities_helper)

    def _setup_yaw_controller(self):
        """Initializes the yaw controller and expected velocities."""
        self.yaw_controller_config = self.param('yaw_controller')
        fpid_controller = PIController(
            k_p=self.yaw_controller_config['kp_velocity'],
            k_i=self.yaw_controller_config['ki_velocity'],
            k_f=self.yaw_controller_config['kf_velocity'],
            pos_limit=self.yaw_controller_config['pos_limit'],
            neg_limit=self.yaw_controller_config['neg_limit'],
            rate=self.rate_hz,
            sat_limit=self.yaw_controller_config['sat_limit'])
        self.yaw_controller = PPositionController(
            kp=self.yaw_controller_config['kp_position'],
            velocity_controller=fpid_controller,
            controller_rate=self.rate_hz,
            inverted_controls=self.yaw_controller_config['inverted_controls'],
            min_control_effort=self.yaw_controller_config['min_control'],
            name='yaw')
        expected_velocities_helper = ExpectedVelocityHelper(self.yaw_controller_config['expected_velocities_file'])
        self.yaw_controller.set_expected_velocity_helper(expected_velocities_helper)

    def _initialize_constants(self):
        self.yaw_reset_arm_height = self.param('vpat_server/calibrate_yaw/raise_arm_height')
        self.yaw_reset_height_error = self.param('vpat_server/calibrate_yaw/raise_arm_height_error')
        self.yaw_deflection = self.param('vpat_server/calibrate_yaw/yaw_effort')

        # Joint limit constants
        self.min_yaw, self.max_yaw = self.param('actuator/blade/limits/yaw_angle_limits')
        self.min_roll, self.max_roll = self.param('actuator/blade/limits/roll_angle_limits')
        self.min_arm_angle, self.max_arm_angle = self.param('actuator/blade/limits/arm_angle_limits')
        self.min_height, self.max_height = self.param('actuator/blade/limits/height_limits')

    def _calc_engine_rpm_scale(self):
        """Controller velocities are based on the max engine RPM.

        The controller gain is adjusted based on the engine RPM so the blade can follow the desired velocity when the
        engine RPMs are lower.
        """
        max_cur_rpm_delta = self.gparam('machine_hw/max_rpm') - self.engine_rpm
        rpm_pressure_scale = self.gparam('machine_hw/rpm_pressure_scale')
        target_rpm = self.engine_rpm + max_cur_rpm_delta * rpm_pressure_scale

        return target_rpm / self.engine_rpm

    def _receive_rpm(self, msg):
        self.engine_rpm = msg.engine_rpm


log = init_blogger(VpatServer)
