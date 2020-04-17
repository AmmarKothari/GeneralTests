import argparse
import pdb
import time

import rospy
from nav_msgs.msg import Odometry

import built
from built.msg import NavigateGoal
from pybuilt.util import bpose, helpers
from pybuilt.vehicle_clients.vehicle_client import VehicleFactory

NAV_GOAL_TOPIC = '/navigate/upstream'
log = helpers.init_blogger('debug_navigates')


def main():
    """Helps with debugging navigates."""
    parser = argparse.ArgumentParser(
        description='Sends a navigate goal with certain parameters relative to current position')
    parser.add_argument(
        '--xy',
        default=[10, 0],
        nargs='+',
        type=list,
        help='Sets the goal xy (meters) as an offset from the current position')
    parser.add_argument(
        '--yaw', default=0, type=float, help='Sets the goal yaw (radians) as an offset from the current orientation')
    parser.add_argument('--speed', default=2.0, type=float, help='Nav goal speed')
    navigate_modes = (NavigateGoal.MODE_PRECISE_FORWARD, NavigateGoal.MODE_PRECISE_BEHIND, NavigateGoal.MODE_HOT,
                      NavigateGoal.MODE_OVERSHOOT, NavigateGoal.MODE_STRAIGHTAWAY)
    parser.add_argument('--mode', default='hot', type=str, choices=navigate_modes, help='Different navigate modes')
    parser.add_argument('--orientation_tol', default=0.5, type=float, help='Orientation tolerance for nav finish')

    args = parser.parse_args()
    pdb.set_trace()
    # vehicle = VehicleFactory.get_vehicle(components=('navigate'))
    # vehicle = VehicleFactory.get_vehicle()

    # current_bp =  vehicle.track_center()
    goal_pub = rospy.Publisher(NAV_GOAL_TOPIC, built.msg.NavigateGoal, queue_size=1, latch=True)

    current_bp = None

    def _receive_velocity(msg):
        if not current_bp:
            current_bp = bpose.BPose(msg.pose)

    odom_sub = rospy.Subscriber('/localizer/odometry', Odometry, callback=_receive_velocity)
    time.sleep(1.0)
    goal_bp_offset = bpose.BPose(xyz=[args.xy[0], args.xy[1], 0], rpy=[0, 0, args.yaw])
    goal_bp = current_bp.relative_add(goal_bp_offset)

    nav_goal = built.msg.NavigateGoal(
        target_pose_s=goal_bp.ros_pose_stamped(),
        speed=args.speed,
        mode=args.mode,
        orientation_tol=args.orientation_tol)
    log.i('Sending Nav Goal: {}'.format(nav_goal))
    res = vehicle.send_navigate(nav_goal).wait_for_result()

    log.i('Result: {}'.format(res))


if __name__ == '__main__':
    main()
