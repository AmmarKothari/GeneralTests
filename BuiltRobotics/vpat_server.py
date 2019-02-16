#!/usr/bin/python
from __future__ import division

import rospy
import time
import numpy as np
import math
import threading

from pybuilt.util.action.action_server import BuiltActionServer
from pybuilt.controls.vehicles.d6.kinematics.d6_imu_helper import D6ImuHelper
from pybuilt.controls.vehicles.d6.joysticks import JsBladeHeightPublisher, JsBladeRollPublisher, JsBladeYawPublisher
from pybuilt.controls.algorithms.fpid import PIController
from pybuilt.controls.util.expected_velocity_helper import ExpectedVelocityHelper
from pybuilt.controls.algorithms.position_controller import PPositionController
from pybuilt.controls.vehicles.d6.kinematics.vpat_model import D6TXLVpatModel
from pybuilt.hardware.drivers.gamepad import Gamepad
from pybuilt.util.action.action_helpers import UPDATE_IN_PLACE_ON_MAIN_THREAD

from pybuilt.util.action.action_state import BuiltActionState
from pybuilt.util.action.action_helpers import READY_STATE_NAME
from pybuilt.util.timing.rate import Rate
from pybuilt.util.helpers import init_blogger, init_node
from pybuilt.util.timing.timer import Timer
from pybuilt.util import btf

from built.msg import VpatGoal, VpatResult, EngineStatistics, D6Imu, D6ControlStatus

CALIBRATE_YAW_STATE = 'calibrate_yaw'
DETERMINE_STATE = 'determine_state'
COMMAND_POSITION_STATE = 'command_position'


class VpatServer(BuiltActionServer):
    """A State Machine responsible for handling all goals related to the blade which includes controlling:

    - Blade height
    - Blade roll
    - Blade yaw

    Blade height and yaw can't be changed at the same time.
    """

    def __init__(self, imu_rate_hz):
        super(VpatServer, self).__init__(VpatGoal, VpatResult)

        self.imu_rate_hz = imu_rate_hz
        self._initialize_constants()
        self.yaw_calibrated = False
        self.state_after_yaw = None
        self.rate_hz = self.param('rate_hz')

        self.imu_helper = D6ImuHelper()
        self.vpat_model = D6TXLVpatModel()

        self.publish_tf_timer = Timer(1.0 / self.gparam('publish_effector_rate_hz'), periodic=True)

        # Message publishers to control blade height, roll, and yaw
        self.blade_height_pub = JsBladeHeightPublisher()
        self.blade_roll_pub = JsBladeRollPublisher()
        self.blade_yaw_pub = JsBladeYawPublisher()

        # Controller setup and status tracking
        self._setup_height_controller()
        self._setup_roll_controller()
        self._setup_yaw_controller()

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

        rospy.Subscriber('/machine_hw/engine_statistics', EngineStatistics, self._receive_rpm, queue_size=1)
        rospy.Subscriber('/machine_hw/control_status', D6ControlStatus, self._receive_control_status, queue_size=1)
        rospy.Subscriber('/imu_reader/imu', D6Imu, self._receive_imu, queue_size=1, tcp_nodelay=True)

        self.lock = threading.RLock()
        self.last_imu_ts = time.time()
        self.cab_bp = None
        self.blade_bp = None
        self.relative_joint_angles = None  # arm angle, yaw angle, roll angle
        self.integrated_yaw_angle = 0
        self.time_spent_yawing = 0
        self.last_time_yaw_driven = time.time()
        self.was_yawing = False

    # --------------------------------------------
    # State methods
    # --------------------------------------------

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
        if not self._is_yaw_expired() and self.yaw_calibrated and next_state_name != VpatGoal.GOAL_TYPE_CALIBRATE_YAW:
            self.request_transition(next_state_name)
        else:
            log.w('Calibrating yaw before moving to state {}'.format(next_state_name))
            self.state_after_yaw = next_state_name
            self.request_transition(CALIBRATE_YAW_STATE)

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

        with self.lock:
            prev_yaw_angle = self.relative_joint_angles[1]

        blade_yaw_timer = Timer(self.param('calibrate_yaw/yaw_movement_expire_time'))
        rate = Rate(self.rate_hz, 'vpat')
        while True:
            with self.lock:
                blade_bp = self.blade_bp
                yaw = self.integrated_yaw_angle

            # Start yawing the blade once the arm height is at or above some height
            if blade_bp.xyz[2] >= self.yaw_reset_arm_height or self._control_vpat_height(blade_bp.xyz[2]):
                if not blade_yaw_timer.running():
                    blade_yaw_timer.start()

                self.blade_yaw_pub.publish_deflection(self.yaw_deflection)

                if self.gamepad.is_override_active():
                    log.w('Override held during calibration, resetting calibration timer', throttle=1.0)
                    blade_yaw_timer.reset()
                    blade_yaw_timer.start()

                if not np.isclose(yaw, prev_yaw_angle, rtol=0):
                    blade_yaw_timer.reset()
                    blade_yaw_timer.start()

                    # Re-run yaw calibration if it's going the wrong way for some weird reason.
                    if not self.gamepad.is_override_active() and yaw < prev_yaw_angle:
                        fail_msg = 'Yaw calibration going the wrong way!!!! curr={} prev={}'.format(yaw, prev_yaw_angle)
                        log.f(fail_msg)
                        self.request_transition(CALIBRATE_YAW_STATE)

                    prev_yaw_angle = yaw

                # Once blade movement hasn't been sensed for some time, the yaw can be considered to be at the hard stop
                if blade_yaw_timer.is_ready():
                    break

            self.sleep_and_yield_rate(rate)

        log.i('Done calibrating yaw.')

        with self.lock:
            self.integrated_yaw_angle = math.radians(self.gparam('blade/limits/yaw_angle_limits')[1])
            self.yaw_calibrated = True
            self.time_spent_yawing = 0
            
        self.request_transition(next_state_name) # skips yaw calibration! -- DON"T MERGE!
        if self.state_after_yaw and self.state_after_yaw != CALIBRATE_YAW_STATE:
            self.request_transition(self.state_after_yaw)
        else:
            self.finish_success()

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
            with self.lock:
                cab_bp = self.cab_bp
                blade_bp = self.blade_bp
                relative_joint_angles = self.relative_joint_angles

            if self.goal.goal_type == VpatGoal.GOAL_TYPE_COMMAND_POSITION_NO_YAW:
                yaw_reached = True
            else:
                yaw_reached = self._control_yaw(math.degrees(relative_joint_angles[1]))

            # Wait until yaw position is reached until doing the height and roll control
            if yaw_reached:
                height_reached = self._control_vpat_height(blade_bp.xyz[2])
                cross_slope_roll = self.vpat_model.cross_slope_roll(cab_bp, blade_bp)
                roll_reached = self._control_cross_slope_roll(math.degrees(cross_slope_roll))
                if yaw_reached and height_reached and roll_reached and not self.goal.maintain:
                    log.d('Success. height {:2.2f} yaw {:2.2f} roll {:2.2f}'.format(
                        blade_bp.xyz[2], self.integrated_yaw_angle, cross_slope_roll))
                    self.finish_success()

            self._check_failure_conditions()
            self.sleep_and_yield_rate(rate)

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
        with self.lock:
            cab_bp = self.cab_bp
            blade_bp = self.blade_bp
            yaw_angle = self.integrated_yaw_angle

        result_msg.cross_slope_angle_degs = math.degrees(self.vpat_model.cross_slope_roll(cab_bp, blade_bp))
        result_msg.yaw_angle_degs = math.degrees(yaw_angle)
        result_msg.center_blade_height = blade_bp.xyz[2]

    def reset_state(self):
        """Resets the state machine to prepare for the next state."""
        self.blade_height_pub.reset()
        self.blade_yaw_pub.reset()
        self.blade_roll_pub.reset()

        self.height_controller.reset()
        self.roll_controller.reset()
        self.yaw_controller.reset()

        self.state_after_yaw = None
        self.goal_timeout.reset()

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

    def _is_yaw_expired(self):
        """Returns True if yaw angle has expired or marked as uncalibrated."""
        return self.time_spent_yawing >= self.param('yaw_expiration_time')

    def publish_static_transforms(self):
        """Publishes static transforms related to VPAT server."""
        btf.send_static_transforms(self.vpat_model.static_transforms)

    # -------------------------------------------------------------
    # Subscriber callbacks
    # -------------------------------------------------------------

    def _receive_imu(self, msg):
        with self.lock:
            stamps = [msg.cab.header.stamp.to_sec(), msg.arm.header.stamp.to_sec(), msg.blade.header.stamp.to_sec()]
            now = time.time()
            oldest_ts = min(stamps)

            # Check latency from IMU message
            if (now - oldest_ts) > self.param('imu_max_latency') and not self.gparam('use_sim', False):
                log.w('IMU latency ={}s', now - oldest_ts)

            # IMU messages -> BPose conversion
            cab_imu_bp = self.imu_helper.bp_from_ros_msg(msg.cab)
            arm_imu_bp = self.imu_helper.bp_from_ros_msg(msg.arm)
            blade_imu_bp = self.imu_helper.bp_from_ros_msg(msg.blade)
            yaw_ang_velocity = msg.blade.angular_velocity.z

            # Integrate yaw if driven within integrate_after_done_yawing_time seconds and yaw angular velocity
            # is over some threshold
            if oldest_ts - self.last_time_yaw_driven <= self.param('integrate_after_done_yawing_time') and \
                    abs(yaw_ang_velocity) > self.param('min_yaw_ang_vel'):
                self.integrated_yaw_angle += math.radians(yaw_ang_velocity) * (now - self.last_imu_ts)

            # Set angles and run FK
            self.relative_joint_angles = self.imu_helper.imu_to_joint_angles(cab_imu_bp, arm_imu_bp, blade_imu_bp,
                                                                             self.integrated_yaw_angle)
            self.vpat_model.angles = self.relative_joint_angles
            self.blade_bp = self.vpat_model.end_effector_bp

            # Publish transform periodically
            if self.publish_tf_timer.is_ready():
                bps = self.vpat_model.kinematic_chain_bps
                for bp in bps:
                    bp.stamp = cab_imu_bp.stamp
                btf.send_transform(self.vpat_model.kinematic_chain_bps)

            self.cab_bp = cab_imu_bp
            self.blade_bp = self.vpat_model.end_effector_bp
            self.last_imu_ts = now

    def _receive_control_status(self, msg):
        with self.lock:
            if abs(msg.blade_yaw_deflection) > 0.05:
                if self.was_yawing:
                    self.time_spent_yawing += time.time() - self.last_time_yaw_driven
                self.last_time_yaw_driven = msg.stamp.to_sec()
                self.was_yawing = True
            else:
                self.was_yawing = False

    def _receive_rpm(self, msg):
        self.engine_rpm = msg.engine_rpm

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
            height_err = self.param('never_satisfied_accuracy/height_err')
            cross_slope_err = self.param('never_satisfied_accuracy/roll_err')
            yaw_err = self.param('never_satisfied_accuracy/yaw_err')
        elif accuracy == VpatGoal.ACCURACY_FINER:
            height_err = self.param('finer_accuracy/height_err')
            cross_slope_err = self.param('finer_accuracy/roll_err')
            yaw_err = self.param('finer_accuracy/yaw_err')
        elif accuracy == VpatGoal.ACCURACY_FINEST:
            height_err = self.param('finest_accuracy/height_err')
            cross_slope_err = self.param('finest_accuracy/roll_err')
            yaw_err = self.param('finest_accuracy/yaw_err')
        else:  # assume rough accuracy
            height_err = self.param('rough_accuracy/height_err')
            cross_slope_err = self.param('rough_accuracy/roll_err')
            yaw_err = self.param('rough_accuracy/yaw_err')

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
        self.yaw_reset_arm_height = self.param('calibrate_yaw/raise_arm_height')
        self.yaw_reset_height_error = self.param('calibrate_yaw/raise_arm_height_error')
        self.yaw_deflection = self.param('calibrate_yaw/yaw_effort')

        # Joint limit constants
        self.min_yaw, self.max_yaw = self.gparam('blade/limits/yaw_angle_limits')
        self.min_roll, self.max_roll = self.gparam('blade/limits/roll_angle_limits')
        self.min_arm_angle, self.max_arm_angle = self.gparam('blade/limits/arm_angle_limits')
        self.min_height, self.max_height = self.gparam('blade/limits/height_limits')

    def _calc_engine_rpm_scale(self):
        """Controller velocities are based on the max engine RPM.

        The controller gain is adjusted based on the engine RPM so the blade can follow the desired velocity when the
        engine RPMs are lower.
        """
        max_cur_rpm_delta = self.gparam('machine_hw/max_rpm') - self.engine_rpm
        rpm_pressure_scale = self.gparam('machine_hw/rpm_pressure_scale')
        target_rpm = self.engine_rpm + max_cur_rpm_delta * rpm_pressure_scale

        return target_rpm / self.engine_rpm


log = init_blogger(VpatServer)

if __name__ == "__main__":
    init_node('vpat_server')
    node = VpatServer(rospy.get_param('imu_rate_hz'))
    node.publish_static_transforms()
    rospy.spin()
