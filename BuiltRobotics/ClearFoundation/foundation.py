import matplotlib.patches as mpatches
import matplotlib.collections as mcollection

from matplotlib import pyplot as plt
from itertools import cycle
import numpy as np
import pdb
from bcolors import bcolors
import shapely.geometry as sg
import shapely.ops as so
import copy
from pad import Pad
from ammar_super import AmmarSuper
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED
import scipy.optimize as sopt

DEBUG = False

COST_MULTIPLIER = {'ungraded_area': 100}

class foundation(AmmarSuper):
	MAX_NUMBER_OF_PADS = 20
	POINTS_DEFINE_PAD = 5

	def __init__(self, radius):
		self.radius = radius
		self.circle = mpatches.Circle((0, 0), self.radius, alpha=0.1)
		self.circle = sg.Point(0, 0).buffer(self.radius)
		self.grid_circles = []
		self.grid_lines = []
		self.color_cycle = cycle('rgby')

	def debug_print(self, arg):
		return
		super().debug_print(DEBUG, arg)

	def draw(self, ax):
		x, y = self.circle.exterior.xy
		ax.fill(x, y, 'b', alpha=0.3)

	def check_polygon(self, polygon_sides):
		if int(polygon_sides) % 2 != 1:
			print(bcolors.FAIL + 'Polygon must have odd number of sides' + bcolors.ENDC)
			return False
		return True

	def get_polygon_props(self, polygon_sides):
		width = 2 * self.radius * np.tan(0.5 * 2 * np.pi / polygon_sides)
		length = 2 * self.polygon_radius(polygon_sides)
		polygon_props = {'sides': polygon_sides,
						 'width': width, 'length': length}
		return polygon_props

	def gen_simple_foundation_pads(self, polygon_props):
		xy_vertices = self.circumscribed_polygon_points(polygon_props['sides'])
		total_points = len(xy_vertices)
		# choose vertice with smallest x component as bl of first rectangle
		first_pt_idx = np.argmin(np.array(xy_vertices)[:, 1])
		# only need to add 1 when its odd
		last_pt_idx = 1 + first_pt_idx + \
			abs(first_pt_idx - np.argmax(np.array(xy_vertices)
										 [:, 1]))  # br of last rectangle
		self.debug_print('{}, {}'.format(first_pt_idx, last_pt_idx))
		pads = []
		for i in range(first_pt_idx, last_pt_idx):
			i_cur = i % total_points
			i_next = (i + 1) % total_points
			sub_pad = Pad(back_left=xy_vertices[i_cur], back_right=xy_vertices[
						  i_next], length=polygon_props['length'])
			pads.append(sub_pad)

		return pads

	def evaluate_pads(self, pads):
		num_pads = len(pads)
		process_dict = dict()
		unprocessed_pad = copy.deepcopy(self.circle)
		for i_pad, pad in enumerate(pads):
			operation_dict = dict()
			operation_dict['pad'] = pad
			operation_dict['length'] = pad.l
			operation_dict['width'] = pad.w
			operation_dict['material_moved'] = pad.l * pad.w * PAD_DEPTH
			operation_dict['num_lanes'] = np.ceil(pad.w / VPAT_WIDTH)
			operation_dict['pushes_per_lane'] = np.ceil(
				pad.l * PAD_DEPTH * VPAT_WIDTH / VPAT_CAPACITY)
			operation_dict['push_start_locs'] = self.linear_interp_between_pts(
				pad.front_center, pad.back_center, operation_dict['pushes_per_lane'])
			operation_dict['dirt_length_per_push'] = pad.l / \
				operation_dict['pushes_per_lane'] * operation_dict['num_lanes']
			total_push_dist = 0
			for i_push, push in enumerate(np.arange(operation_dict['pushes_per_lane'])):
				total_push_dist += i_push * \
					operation_dict['dirt_length_per_push']
			operation_dict['total_push_dist'] = total_push_dist
			operation_dict['lane_time'] = operation_dict[
				'total_push_dist'] / PUSH_SPEED + operation_dict['total_push_dist'] / REVERSE_SPEED
			on_foundation_lane = pad.poly.intersection(self.circle)
			operation_dict['area_foundation_cleared'] = on_foundation_lane.area
			operation_dict['area_outside_foundation'] = pad.poly.difference(
				self.circle).area
			newly_graded_area = unprocessed_pad.area - \
				unprocessed_pad.difference(on_foundation_lane).area
			operation_dict[
				'area_regraded'] = on_foundation_lane.area - newly_graded_area
			unprocessed_pad = unprocessed_pad.difference(pad.poly)
			process_dict[i_pad] = copy.deepcopy(operation_dict)
		return process_dict, unprocessed_pad

	def grading_process_stats(self, process_dict, unprocessed_pad):
		average_length = np.mean([process['length']
								  for process in process_dict.values()])
		average_width = np.mean([process['width']
								 for process in process_dict.values()])
		total_material = np.sum([process['material_moved']
								 for process in process_dict.values()])
		total_time = sum([process['lane_time']
						  for process in process_dict.values()])
		total_regrade = sum([process['area_regraded']
							 for process in process_dict.values()])
		total_lanes = sum([process['num_lanes']
							 for process in process_dict.values()])
		pad_transition_dist = 0
		for i_process in range(1, len(process_dict.values()) - 1):
			pad_transition_dist += np.linalg.norm(process_dict[i_process][
												  'push_start_locs'][-1] - process_dict[i_process + 1]['push_start_locs'][0])
		total_dist = sum([process['total_push_dist']
						  for process in process_dict.values()]) + pad_transition_dist
		total_area = self.circle.area
		grading_stats_dict = {'average_length': average_length, 'average_width': average_width, 'total_material': total_material, 'total_time': total_time, 'total_regrade': total_regrade,
					  'pad_transition_dist': pad_transition_dist, 'total_dist': total_dist, 'total_area': total_area, 'total_lanes': total_lanes,
					  'ungraded_area':unprocessed_pad.area}
		# print('Pad Width: {average_width:.2f} m, Pad Length: {average_length:.2f} m, Total Lanes: {total_lanes:.0f}'.format(**grading_stats_dict))
		# print('Pad Depth: {:.2f} m, Total Material: {:.2f} Ungraded Area: {:.2f}, m^3, Total Dist: {:.2f} (Pad Transition Dist: {:.2f}%), Total Regrade: {:.2f} ({:.2f}%), Estimated Time: {:.0f} sec ({:.2f} min)'.format(
		# 	PAD_DEPTH, total_material, unprocessed_pad.area, total_dist, pad_transition_dist / total_dist * 100, total_regrade, total_regrade / total_area * 100, total_time, total_time / 60))
		print('Ungraded Area: {:.2f} m^3, Total Regrade: {:.2f} %'.format(unprocessed_pad.area, total_regrade / total_area * 100))
		return grading_stats_dict

	def grading_score(self, process_dict, grading_stats_dict):
		total_graded_poly = so.cascaded_union(
			[p['pad'].poly for p in process_dict.values()])
		total_useful_graded = self.circle.area - \
			self.circle.difference(total_graded_poly).area
		grade_score = - COST_MULTIPLIER['ungraded_area'] * grading_stats_dict['ungraded_area'] \
		- grading_stats_dict['total_regrade'] \
		- grading_stats_dict['total_dist'] + total_useful_graded
		return grade_score

	# this and the above function are the same except for how the indexes are
	# calculated
	def hex_grid_one_side(self, polygon_sides, ax, draw=False):
		# slot doze so that all the spoil piles end up on one side
		if not self.check_polygon(polygon_sides):
			raise ValueError
		self.draw_polygon(self.circumscribed_polygon_points(polygon_sides), ax)

		end_lines = []
		polygon_props = self.get_polygon_props(polygon_sides)
		pads = self.gen_simple_foundation_pads(polygon_props)
		process_dict, unprocessed_pad = self.evaluate_pads(pads)

		self.draw_multipolygon(unprocessed_pad, ax)
		[self.draw_pad(pad.poly, ax) for pad in pads]
		grading_stats_dict = self.grading_process_stats(
			process_dict, unprocessed_pad)
		grade_score = self.grading_score(process_dict, grading_stats_dict)

		print('Grade Score: {:.2f}'.format(grade_score))

		return end_lines


	######################
	# Optimization Methods
	######################

	def optimize_hex_grid_one_side(self, ax, draw=False):
		# generate a set of pads (probably through picking a center back point,
		# a center front point, and a width)
		# a pad = (bl_x, bl_y, fl_x, fl_y, width)
		# initial_guess = np.random.rand(self.POINTS_DEFINE_PAD, self.MAX_NUMBER_OF_PADS)

		polygon_props = self.get_polygon_props(self.MAX_NUMBER_OF_PADS)
		regular_pads = self.gen_simple_foundation_pads(polygon_props)
		initial_guess = np.array([[p.bl[0], p.bl[1], p.fl[0], p.fl[1], p.w] for p in regular_pads])
		initial_guess_vec = self.vectorify(initial_guess)
		self.iter_count = 0
		res = sopt.minimize(self.opt_eval_pads, initial_guess_vec, method='nelder-mead',options={'xtol': 1e-8, 'disp': True}, callback=self.print_iteration_info)
		pdb.set_trace()

	def print_iteration_info(self, Xi):
		print('Iteration: {}, Score: {:.2f}'.format(self.iter_count, self.opt_eval_pads(Xi)))
		self.iter_count += 1

	def vectorify(self, array):
		"""Turns an array in to a vector for optimization purposes"""
		return array.reshape(-1)

	def arrayify(self, vector):
		"""turns a vector into an array for optimization purposes"""
		return vector.reshape(-1, self.POINTS_DEFINE_PAD)

	def opt_eval_pads(self, pads_guess):
		"""Function that evaluates a set of guesses"""
		pads_array = self.arrayify(pads_guess)
		pads = [Pad(back_left = p[0:2], front_left = p[2:4], width = p[4]) for p in pads_array]
		# pdb.set_trace()
		# need a step here to convert points into pad objects!
		process_dict, unprocessed_pad = self.evaluate_pads(pads)
		grading_stats_dict = self.grading_process_stats(process_dict, unprocessed_pad)
		# will minimize so want to return positive scores -- need to check cost function
		grade_score = -1*self.grading_score(process_dict, grading_stats_dict)
		return grade_score


		

	##################
	# Helper Methods
	##################

	def circumscribed_polygon_points(self, polygon_sides):
		xy = []
		angle = self.polygon_angle(polygon_sides)
		dist_to_vertex = self.polygon_radius(polygon_sides)
		for i in range(polygon_sides):
			xy.append(
				[dist_to_vertex * np.sin(np.pi * 2 * (float(i)) / polygon_sides),
				 dist_to_vertex * np.cos(np.pi * 2 * (float(i)) / polygon_sides)]
			)
		return xy

	def polygon_side_length(self, polygon_sides):
		angle = self.polygon_angle(polygon_sides)
		dist_to_vertex = self.radius / np.cos(angle)
		side_length = 2 * np.sqrt(dist_to_vertex**2 - self.radius ** 2)
		return side_length

	def polygon_radius(self, polygon_sides):
		# distance from vertex to center
		angle = self.polygon_angle(polygon_sides)
		return self.radius / np.cos(angle)

	def polygon_angle(self, polygon_sides):
		return np.pi / polygon_sides

	def draw_polygon(self, points, ax):
		# draw a polygon from points
		x, y = sg.Polygon(points).exterior.xy
		plt.plot(x, y, alpha=0.2, linewidth=3, color='k')

	def rectangle(self, xytlw):
		x, y, t, l, w = xytlw
		rect_xy = sg.Polygon(np.hstack((x, y))).exterior.xy
		return rect_xy

	def rectangle_patch(self, xytlw):
		x, y, t, l, w = xytlw
		self.rectangle(xytlw)
		rectangle = mpatches.Rectangle([0, 0],
									   -w,
									   l,
									   angle=np.rad2deg(t),
									   fill=False,
									   color=next(self.color_cycle))
		rectangle._x0 = x
		rectangle._y0 = y
		rectangle._update_x1()
		rectangle._update_y1()
		return rectangle

	def draw_arrow(self, xytl):
		if type(xytl) is sg.Polygon:
			x, y = self.front_center(xytl)
			dx, dy = self.back_center(xytl)
		else:
			x, y, t, l = xytl
			dx = np.cos(t + np.pi / 2) * l
			dy = np.sin(t + np.pi / 2) * l
		plt.arrow(x, y, dx, dy, head_width=1)

	def draw_endline(self, rectangle):
		F = np.array(rectangle.exterior.xy)[2:4]
		plt.plot(F[:, 0], F[:, 1], 'k:', linewidth=3.0)

	def draw_pad(self, rectangle, ax):
		x, y = rectangle.exterior.xy
		ax.plot(x, y, color=next(self.color_cycle))
		self.draw_arrow(rectangle)
		self.draw_endline(rectangle)
		plt.axis('auto')
		plt.draw()

	def draw_multipolygon(self, multipoly, ax):
		for p in multipoly:
			x, y = p.exterior.xy
			ax.plot(x, y, 'r:')

	def front_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[0:2], axis=0)

	def back_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[2:4], axis=0) - self.front_center(rectangle)

	def linear_interp_between_pts(self, start_pt, end_pt, num_points):
		interp_points = [np.linspace(start_pt[i], end_pt[i], int(
			num_points)) for i in range(len(start_pt))]
		return np.array(interp_points).T

	def plot_multipoly(self, multi_poly):
		xs = []
		ys = []
		colors = cycle('rgb')
		for poly in multi_poly:
			x = np.array(poly.exterior.xy[0])
			y = np.array(poly.exterior.xy[1])
			# xs.append(x)
			# ys.append(y)
			plt.plot(x, y, '{}x-'.format(colors.next()))
		# xs = np.hstack(xs)
		# ys = np.hstack(ys)

		plt.show()

	def plot_multiple_pads(self, pads_list):
		for pad in pads_list:
			x,y = pads.poly.exterior.xy
			plt.plot(x,y, 'x-')
		plt.show()


if __name__ == '__main__':
	FOUNDATION_DIAMETER = 2*160 * 12 * 2.54 / 100  # foundation diameter at bottom in m
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	# f1.hex_grid_one_side(11, ax1)
	f1.optimize_hex_grid_one_side(ax1)
	plt.show()
