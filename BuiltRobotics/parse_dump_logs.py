import io
import re
import pdb
import numpy as np
import matplotlib.pyplot as plt
import pybuilt.util.bviz as bviz
from pybuilt.util import color


# COMMAND USED TO GET DATA
# grep -a -e "Terrain map" -e "Dump Finder" -e "xza0" combined_logs.txt > combined_logs_reduced.txt


# INPUT_FN = 'combined_logs_reduced.txt'
import rospy

INPUT_FN = 'bstdout_combined.txt'

point_finder_re = 'X:\s*(\d+.\d+) Y:\s*(\d+.\d+) Z:\s*(\d+.\d+)'

DUMP_FINDER_PT_TYPE = 'dump_finder'
TERRAIN_MAP_UPDATE_PT_TYPE = 'terain_map_update'
DUMP_PLANNER_PT_TYPE = 'dump_planner'

MARKER_LIFETIME = 10
VIZ_SQUARE_DIM = 0.5
COUNT_TO_SHOW_TEXT = 10

def get_pts_from_file():
	last_pt_type = None
	dump_pts = []
	terrain_map_pts = []

	multiple_dump_pts_without_terrain_update = 0
	with io.open(INPUT_FN) as input_file:
		for row in input_file:
			try:
				point_groups = re.search(point_finder_re, row).groups()
			except AttributeError:
				continue
			pt = np.array(point_groups).astype('float')
			if 'Dump Finder' in row:
				if last_pt_type == DUMP_FINDER_PT_TYPE:
					dump_pts.pop(-1)
					multiple_dump_pts_without_terrain_update += 1
				dump_pts.append(pt)
				last_pt_type = DUMP_FINDER_PT_TYPE
			else:
				terrain_map_pts.append(pt)
				last_pt_type = TERRAIN_MAP_UPDATE_PT_TYPE
	if len(dump_pts) > len(terrain_map_pts):
		dump_pts.pop(-1)
	dump_pts = np.array(dump_pts)
	terrain_map_pts = np.array(terrain_map_pts)
	return dump_pts, terrain_map_pts


def _print_point_selection_stats(dump_pts, terrain_map_pts):

	print('Num Dump Points: {}'.format(len(dump_pts)))
	print('Num Terrain Map Points: {}'.format(len(terrain_map_pts)))
	unique_dump_pts, count_unique_dump_pts = np.unique(dump_pts[:, :2], axis=0, return_counts=True)
	print('Average time a point is choosen: {:.3f}'.format(np.mean(count_unique_dump_pts)))
	print('Max count a point is choosen: {}'.format(np.max(count_unique_dump_pts)))
	print('Min count a point is choosen: {}'.format(np.min(count_unique_dump_pts)))
	pt_diffs = dump_pts - terrain_map_pts
	avg_xy_dist = np.mean(np.linalg.norm(pt_diffs[:, :2], axis=1))
	avg_x_dist = np.mean(np.abs(pt_diffs[:, 0]))
	avg_y_dist = np.mean(np.abs(pt_diffs[:, 1]))
	max_x_dist = np.max(np.abs(pt_diffs[:, 0]))
	max_y_dist = np.max(np.abs(pt_diffs[:, 1]))
	max_xy_dist = np.max(np.linalg.norm(pt_diffs[:, :2], axis=1))
	min_x_dist = np.min(np.abs(pt_diffs[:, 0]))
	min_y_dist = np.min(np.abs(pt_diffs[:, 1]))
	min_xy_dist = np.min(np.linalg.norm(pt_diffs[:, :2], axis=1))
	print('Average xy distance (dump - tmap): {:.3f}'.format(avg_xy_dist))
	print('Average x  distance (dump - tmap): {:.3f}'.format(avg_x_dist))
	print('Average y  distance (dump - tmap): {:.3f}'.format(avg_y_dist))
	print('Max X Distance: {:.3f}'.format(max_x_dist))
	print('Max Y Distance: {:.3f}'.format(max_y_dist))
	print('Max XY Distance: {:.3f}'.format(max_xy_dist))
	print('Min X Distance: {:.3f}'.format(min_x_dist))
	print('Min Y Distance: {:.3f}'.format(min_y_dist))
	print('Min XY Distance: {:.3f}'.format(min_xy_dist))
	return count_unique_dump_pts, unique_dump_pts


def _plot_points_matplotlib():
	plt.plot(dump_pts[:, 0], dump_pts[:, 1], 'rx', label='dump points')
	plt.plot(terrain_map_pts[:, 0], terrain_map_pts[:, 1], 'bo', label='terrain map pts')
	for dump_pt, terrain_map_pt in zip(dump_pts, terrain_map_pts):
		combined_pts = np.vstack((dump_pt, terrain_map_pt))
		plt.plot(combined_pts[:, 0], combined_pts[:, 1], 'k-')
	# plot text for the number of times a point was selected
	points_picked_many_times = unique_dump_pts[count_unique_dump_pts > 10]
	count_points_picked_many_times = count_unique_dump_pts[count_unique_dump_pts > 10]
	for count, pt in zip(count_points_picked_many_times, points_picked_many_times):
		plt.text(pt[0], pt[1], str(count))
	plt.legend(loc='center')
	plt.axis('equal')
	plt.show()

def _plot_uniqueness_histogram():


def _plot_points_rviz():
	# bviz.show_sphere_list(dump_pts, lifetime_s=MARKER_LIFETIME, frame='map', radius=0.25, rgbas=color.Color.RED)
	# for dump_pt, terrain_map_pt in zip(dump_pts, terrain_map_pts):
	# 	bviz.show_sphere(xyz=dump_pt, lifetime_s=MARKER_LIFETIME, frame='map', radius=0.25, rgba=color.Color.RED)

	unique_dump_pts, unique_idxs, count_unique_dump_pts = np.unique(dump_pts[:, :2], axis=0, return_counts=True, return_index=True)
	for ct, pt in zip(count_unique_dump_pts, dump_pts[unique_idxs]):
		if ct > COUNT_TO_SHOW_TEXT:
			bviz.show_text(pt, str(ct), lifetime_s=MARKER_LIFETIME)

		# bviz.show_box(xyz=terrain_map_pt, lifetime_s=MARKER_LIFETIME, length=VIZ_SQUARE_DIM, width=VIZ_SQUARE_DIM, height=VIZ_SQUARE_DIM, rgba=color.Color.BLUE)

dump_pts, terrain_map_pts = get_pts_from_file()
count_unique_dump_pts, unique_dump_pts = _print_point_selection_stats(dump_pts, terrain_map_pts)
_plot_points_matplotlib()


def main():
	rospy.init_node('measured_points_vis')
	bviz.clear_all()
	try:
		while not rospy.is_shutdown():
			_plot_points_rviz()
			rospy.sleep(MARKER_LIFETIME)
	except KeyboardInterrupt:
		pass
	finally:
		print('Stopping publishing of points')


if __name__ == '__main__':
    main()
