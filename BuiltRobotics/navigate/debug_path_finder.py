import math

from pybuilt.perception.util.nav_obstacle_map_factory import NavObstacleMapFactory
from pybuilt.planning.circle_straight_path.circle_straight_path_finder import CircleStraightPathFinder
from pybuilt.planning.hybrid_a_star.hybrid_a_star_path_finder import HybridAStarPathFinder
from pybuilt.planning.rs.reeds_shepp_path_finder import ReedsSheppPathFinder
from pybuilt.planning.util.obstacle_check import ObstacleCheck
from pybuilt.util import bnum
from pybuilt.util.helpers import init_blogger
from pybuilt.planning.path_finder import PathFinder

import pdb
import numpy as np
import matplotlib.pyplot as plt

SCALE = 0.2


def pprint_path(path):
    for wp in path:
        print('{:.3f}, {:.3f}, {:.3f}'.format(*wp))


def print_path_error(path, target_wp):
    error = [x - y for x, y in zip(path[-1], target_wp)]
    print('Errors -- X: {:.3f}, {:.3f}, {:.3f}'.format(error[0], error[1], error[2]))


def plot_wp(waypoint, marker='rx', ec='k'):
    plt.arrow(waypoint[0], waypoint[1], np.cos(waypoint[2]) * SCALE, np.sin(waypoint[2]) * SCALE, ec=ec)
    plt.plot(waypoint[0], waypoint[1], marker)


def plot_path(path, ec='k'):
    for wp in path:
        plot_wp(wp, ec=ec)


def cs_test():
    obstacle_map_factory = NavObstacleMapFactory()
    obstacle_snapshot = obstacle_map_factory.snapshot()
    obstacle_check = ObstacleCheck(obstacle_snapshot)
    cs_path_segment = CircleStraightPathFinder.get_path(start_wp, target_wp, obstacle_check)
    print_path_error(cs_path_segment, target_wp)
    plot_path(cs_path_segment)
    plot_wp(target_wp, 'bo')

    plt.gca().set_ylim(0, 10)
    plt.show()


def rs_test():
    start_wp = [0, 0, 0]
    target_wp_inline = [10, 0, 0]
    target_wp_opposite = [10, 0, np.pi]
    orientation_tol = 0.1

    obstacle_map_factory = NavObstacleMapFactory()
    obstacle_snapshot = obstacle_map_factory.snapshot()
    obstacle_check = ObstacleCheck(obstacle_snapshot)

    rs_path_finder = ReedsSheppPathFinder()
    pdb.set_trace()
    # Front Back agnostic is False
    path_len, target_wp_inline_shortest = rs_path_finder.calc_shortest_path_len(
        start_wp,
        target_wp_inline,
        # orientation_tol=orientation_tol,
        front_back_agnostic=False)
    rs_path_segment_inline = rs_path_finder.get_path(start_wp, target_wp_inline_shortest, obstacle_check)

    print('Front Back Agnostic: {}'.format(False))
    print('Original Waypoint: {}, Shortest Path Waypoint: {}'.format(target_wp_inline, target_wp_inline_shortest))
    print_path_error(rs_path_segment_inline, target_wp_inline)
    print('Path Length: {}'.format(path_len))
    plot_path(rs_path_segment_inline)
    plot_wp(target_wp_inline, 'bo')

    # flipping target point by pi when agnostic
    path_len, target_wp_opposite_shortest = rs_path_finder.calc_shortest_path_len(
        start_wp,
        target_wp_opposite,
        # orientation_tol=orientation_tol,
        front_back_agnostic=True)
    rs_path_segment_opposite = rs_path_finder.get_path(start_wp, target_wp_opposite_shortest, obstacle_check)
    print('Front Back Agnostic: {}'.format(True))
    print('Original Waypoint: {}, Shortest Path Waypoint: {}'.format(target_wp_opposite, target_wp_opposite_shortest))
    print_path_error(rs_path_segment_opposite, target_wp_opposite)
    print('Path Length: {}'.format(path_len))
    plot_path(rs_path_segment_opposite)
    plot_wp(target_wp_opposite, 'bo')

    plt.gca().set_ylim(0, 10)
    plt.show()


def a_star_test():
    start_wp = [0, 0, 0]
    target_wp_inline = [10, 0, 0]
    target_wp_opposite = [10, 0, np.pi]
    orientation_tol = 0.1
    dist_tol = 0.5

    obstacle_map_factory = NavObstacleMapFactory()
    obstacle_snapshot = obstacle_map_factory.snapshot()
    obstacle_check = ObstacleCheck(obstacle_snapshot)
    goal_wp = None
    a_star_path = HybridAStarPathFinder().get_path(start_wp, target_wp_opposite, obstacle_snapshot, obstacle_check,
                                                   goal_wp, dist_tol, orientation_tol)
    print_path_error(a_star_path, target_wp_opposite)
    plot_path(a_star_path)
    plot_wp(target_wp_opposite, 'bo')

    plt.gca().set_ylim(0, 10)
    plt.show()

    # PathFinder Paths
    # pf = PathFinder()
    # obstacle_map_factory = NavObstacleMapFactory()
    # obstacle_snapshot = obstacle_map_factory.snapshot()
    # obstacle_check = ObstacleCheck(obstacle_snapshot)
    #
    # for t_wp, ec in zip([target_wp, [target_wp[0], target_wp[1], target_wp[2] + np.pi]], ['r', 'b']):
    #     path_finder_path = pf.get_path(start_wp, t_wp, obstacle_snapshot, orientation_tol=orientation_tol)
    #     print_path_error(path_finder_path, t_wp)
    #     plot_path(path_finder_path,  ec=ec)
    #     break
    # plot_wp(target_wp, 'bo')

    # plt.gca().set_ylim(0, 10)
    # plt.show()


def compare_path_tests():
    target_wps = ([10, 0, 0], [10, 0, 3.14], [0, 10, 0], [0, 10, 3.14])

    obstacle_map_factory = NavObstacleMapFactory()  # publish an obstacle!
    obstacle_snapshot = obstacle_map_factory.snapshot()
    obstacle_check = ObstacleCheck(obstacle_snapshot)
    goal_wp = None

    for target_wp in target_wps:
        cs_path_segment = CircleStraightPathFinder.get_path(start_wp, target_wp, obstacle_check)

        rs_path_finder = ReedsSheppPathFinder()
        _, target_wp_shortest = rs_path_finder.calc_shortest_path_len(
            start_wp, target_wp, orientation_tol=orientation_tol)
        rs_path_segment = rs_path_finder.get_path(start_wp, target_wp_shortest, obstacle_check)

        a_star_path = HybridAStarPathFinder().get_path(start_wp, target_wp, obstacle_snapshot, obstacle_check, goal_wp,
                                                       dist_tol, orientation_tol)

        plot_path(cs_path_segment, ec='b')
        plot_path(rs_path_segment, ec='g')
        plot_path(a_star_path, ec='r')
        plot_wp(target_wp, 'bo')
        plt.gca().set_ylim(0, 10)
        plt.show()


# start_wp = [0, 0, 0]
# target_wp = [10, 0, 0]
# orientation_tol = 0.0
# dist_tol = 0.5

# Circle Straight Paths
# cs_test()

# Reed Shepps Paths
rs_test()

# A Star Paths

# compare_path_tests()

pdb.set_trace()
