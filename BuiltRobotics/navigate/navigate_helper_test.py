import numpy as np

from pybuilt.actions.node.core import navigate_helper


def test_get_speed_scale():
    speed_scale_min = 0.75
    yaw_errors = np.linspace(0, np.pi / 2, 100)
    speed_scales = []
    for yaw_error in yaw_errors:
        speed_scale = navigate_helper.get_speed_scale(speed_scale_min, yaw_error)
        speed_scales.append(speed_scale)

    import matplotlib.pyplot as plt
    plt.plot(yaw_errors, speed_scales, 'rx-')
    out = plt.gca()
    out.axvline(x=navigate_helper.SPEED_SCALE_FILTER_CUTOFF, label='Filter Cutoff')
    plt.title('Speed Scale Calculation')
    plt.xlabel('Yaw Error (rads)')
    plt.ylabel('Speed Scale')
    plt.legend()
    plt.show()


def test_get_raw_speed():
    decel_radius = 1.0
    dists_to_goal = np.linspace(2.0, 0.0, 21)
    raw_speeds = []
    goal_speed = 0.5 * 2.0
    max_allowable_speed = 1.8
    for dist_to_goal in dists_to_goal:
        raw_speed = navigate_helper.get_raw_speed(goal_speed, max_allowable_speed, dist_to_goal, decel_radius)
        raw_speeds.append(raw_speed)
    import matplotlib.pyplot as plt

    plt.title('Raw speed calculation')
    plt.xlabel('Distance to goal (m)')
    plt.ylabel('Raw Speed (m/s)')

    plt.plot(dists_to_goal, raw_speeds, 'x-')

    out = plt.gca()
    out.axvline(x=decel_radius, label='Decel Radius', color='k')
    out.axhline(y=goal_speed, label='Goal Speed', color='g')
    out.axhline(y=max_allowable_speed, label='Max Allowable Speed', color='r')
    plt.legend()
    plt.show()
