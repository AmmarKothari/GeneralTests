from pybuilt.perception.util.nav_obstacle_map_factory import NavObstacleMapFactory
from pybuilt.planning.hybrid_a_star.hybrid_a_star_path_finder import HybridAStarPathFinder
from pybuilt.planning.util.obstacle_check import ObstacleCheck

import cProfile
import pstats

"""
Quantitative assessment of how fast A* is running and some profiling information.
Due to variations in runtime environments, this cannot be a direct comparison but should be relatively similar.


Note: pstats module needs to be changed so more sigfigs are printed out
Update the f8 function as below:
def f8(x):
    return "%8.9f" % x
"""

OUTPUT_FILE = '/tmp/a_star_profile'
N = 10

for i in range(N):
    test_a_finder = HybridAStarPathFinder()
    cProfile.run('test_a_finder.get_path((20, 20, 0), (22, 22, 3.14), None, ObstacleCheck(NavObstacleMapFactory().snapshot()))', OUTPUT_FILE + '_{}'.format(i))
stats = pstats.Stats()
for i in range(N):
    stats.add(OUTPUT_FILE + '_{}'.format(i))

print('Total nodes expanded: {}'.format(test_a_finder.num_expanded_nodes))
print('Number of runs: {}'.format(N))
print('Time per node: {:.6f}'.format(stats.total_tt/N/test_a_finder.num_expanded_nodes))
print(stats.sort_stats('time').print_stats(20).sort_stats('name'))