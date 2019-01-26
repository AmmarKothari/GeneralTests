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
# from pad import Pad
from ammar_super import AmmarSuper
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED

DEBUG = False

class foundation(AmmarSuper):
	def __init__(self, radius):
		self.radius = radius
		self.circle = mpatches.Circle( (0,0), self.radius, alpha=0.1)
		self.circle = sg.Point(0,0).buffer(self.radius)
		self.grid_circles = []
		self.grid_lines = []
		self.color_cycle = cycle('rgby')

	def debug_print(self, arg):
		super().debug_print(DEBUG, arg)

	def draw(self, ax):
		x,y = self.circle.exterior.xy
		ax.fill(x,y, 'b', alpha=0.3)

	def check_polygon(self, polygon_sides):
		if int(polygon_sides)%2 != 1:
			print(bcolors.FAIL + 'Polygon must have odd number of sides' + bcolors.ENDC)
			return False
		return True

	def hex_grid_one_side(self, polygon_sides, ax, draw=False): # this and the above function are the same except for how the indexes are calculated
		# slot doze so that all the spoil piles end up on one side
		if self.check_polygon(polygon_sides):
			return
		self.draw_polygon(self.circumscribed_polygon_points(polygon_sides), ax)
		
		pads = []
		end_lines = []
		first_pt_idx = np.argmin(np.array(xy)[:,1]) # bl of first rectangle
		last_pt_idx = first_pt_idx + abs(first_pt_idx - np.argmax(np.array(xy)[:,1])) # br of last rectangle
		self.debug_print('{}, {}'.format(first_pt_idx, last_pt_idx))
		width = 2*self.radius * np.tan(0.5*2*np.pi/polygon_sides)
		length = 2*self.polygon_radius(polygon_sides)

		for i in range(first_pt_idx, last_pt_idx):
			i_cur = i % len(xy)
			i_next = (i+1) % len(xy)

			BL = xy[i_cur]
			BR = xy[i_next]
			theta = np.arctan2(BR[1] - BL[1], BR[0] - BL[0]) - np.pi/2
			FL = [xy[i_cur][0] + np.cos(theta)*length, xy[i_cur][1] + np.sin(theta)*length]
			FR = [xy[i_next][0] + np.cos(theta)*length, xy[i_next][1] + np.sin(theta)*length]
			
			pads.append(sg.Polygon([BL, BR, FR, FL]))
			# pads.append(Pad(BL, BR, length))
			self.debug_print('BL: {}, FR: {}, theta: {}, length: {}, width: {}'.format(BL, FR, theta, length, width))
			if draw:
				self.draw_pad(pads[-1], ax)

		num_pads = last_pt_idx - first_pt_idx
		pad_length = 2*self.polygon_radius(polygon_sides)

		process_dict = dict()
		unprocessed_pad = copy.deepcopy(self.circle)
		for i_pad, pad in enumerate(pads):
			operation_dict = dict()
			operation_dict['rectangle'] = pad
			operation_dict['num_lanes'] = np.ceil(width/VPAT_WIDTH)
			operation_dict['pushes_per_lane'] = np.ceil(length*PAD_DEPTH*VPAT_WIDTH/VPAT_CAPACITY)
			operation_dict['push_start_locs'] = np.linspace(self.front_center(pad), self.back_center(pad), operation_dict['pushes_per_lane'])
			operation_dict['dirt_length_per_push'] = length/operation_dict['pushes_per_lane']
			total_push_dist = 0
			for i_push, push in enumerate(np.arange(operation_dict['pushes_per_lane'])):
				total_push_dist += i_push*operation_dict['dirt_length_per_push']
			operation_dict['total_push_dist'] = total_push_dist
			operation_dict['lane_time'] = operation_dict['total_push_dist'] / PUSH_SPEED + operation_dict['total_push_dist'] / REVERSE_SPEED
			on_foundation_lane = pad.intersection(unprocessed_pad)
			operation_dict['area_foundation_cleared'] = on_foundation_lane.area
			operation_dict['area_outside_foundation'] = pad.difference(self.circle).area
			operation_dict['area_regraded'] = on_foundation_lane.area - unprocessed_pad.difference(on_foundation_lane).area
			unprocessed_pad = unprocessed_pad.difference(pad)
			process_dict[i_pad] = copy.deepcopy(operation_dict)

		total_time = sum([process[1]['lane_time'] for process in process_dict.items()])
		total_regrade = sum([process[1]['area_regraded'] for process in process_dict.items()])
		pad_transition_dist = 0
		for i_process in range(1, len(process_dict.items())-1):
			pad_transition_dist += np.linalg.norm(
				np.vstack(
					(process_dict[i_process]['push_start_locs'][-1],process_dict[i_process+1]['push_start_locs'][0])
					))
		total_dist = sum([process[1]['total_push_dist'] for process in process_dict.items()])
		total_area = self.circle.area
		total_material = width*length*PAD_DEPTH

		print('Pad Width: {:.2f} m, Pad Length: {:.2f} m, Pad Depth: {:.2f} m, Total Material: {:.2f} m^3, Total Dist: {:.2f} (Pad Transition Dist: {:.2f}%), Total Regrade: {:.2f} ({:.2f}%), Estimated Time: {:.0f} sec ({:.2f} min)'.format(
			width, length, PAD_DEPTH, total_material, total_dist, pad_transition_dist/total_dist*100, total_regrade, total_regrade/total_area*100, total_time, total_time/60))
		
		total_graded = self.circle.area - self.circle.difference(so.cascaded_union([p[1]['rectangle'] for p in process_dict.items()])).area
		grade_score = - total_regrade - total_dist - pad_transition_dist + total_graded
		pdb.set_trace()
		print('Grade Score: {:.2f}'.format(grade_score))

		return end_lines


	##################
	# Helper Methods
	##################

	def circumscribed_polygon_points(self, polygon_sides):
		xy = []
		angle = self.polygon_angle(polygon_sides)
		dist_to_vertex = self.polygon_radius(polygon_sides)
		for i in range(polygon_sides):
			xy.append(
				[ dist_to_vertex*np.sin(np.pi*2 * (float(i))/polygon_sides), 
				  dist_to_vertex*np.cos(np.pi*2 * (float(i))/polygon_sides)]
				)
		return xy

	def polygon_side_length(self, polygon_sides):
		angle = self.polygon_angle(polygon_sides)
		dist_to_vertex = self.radius / np.cos(angle)
		side_length = 2 * np.sqrt(dist_to_vertex**2 - self.radius **2)
		return side_length

	def polygon_radius(self, polygon_sides):
		# distance from vertex to center
		angle = self.polygon_angle(polygon_sides)
		return self.radius / np.cos(angle)

	def polygon_angle(self, polygon_sides):
		return np.pi / polygon_sides

	def draw_polygon(self, points, ax):
		# draw a polygon from points
		x,y = sg.Polygon(points).exterior.xy
		plt.plot(x, y, alpha = 0.2, linewidth=3, color='k')

	def rectangle(self, xytlw):
		x, y, t, l, w = xytlw
		rect_xy = sg.Polygon(np.hstack((x,y))).exterior.xy
		return rect_xy

	def rectangle_patch(self, xytlw):
		x, y, t, l, w = xytlw
		self.rectangle(xytlw)
		rectangle = mpatches.Rectangle([0,0],
			-w,
			l,
			angle = np.rad2deg(t),
			fill = False,
			color=next(self.color_cycle))
		rectangle._x0 = x
		rectangle._y0 = y
		rectangle._update_x1()
		rectangle._update_y1()
		return rectangle

	def draw_arrow(self, xytl):
		if type(xytl) is sg.Polygon:
			x,y = self.front_center(xytl)
			dx, dy = self.back_center(xytl)
		else:
			x, y, t, l = xytl
			dx = np.cos(t + np.pi/2)*l
			dy = np.sin(t + np.pi/2)*l
		plt.arrow(x, y, dx, dy, head_width=1)

	def draw_endline(self, rectangle):
		F = np.array(rectangle.exterior.xy)[2:4]
		plt.plot(F[:,0], F[:,1], 'k:', linewidth = 3.0)

	def draw_pad(self, rectangle, ax):
		x,y = rectangle.exterior.xy
		ax.plot(x,y,color=next(self.color_cycle))
		self.draw_arrow(rectangle)
		self.draw_endline(rectangle)
		plt.axis('auto')
		plt.draw()

	def draw_multipolygon(self, multipoly, ax):
		for p in multipoly:
			x,y = p.exterior.xy
			ax.plot(x,y, 'r:')

	def front_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[0:2], axis=0)

	def back_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[2:4], axis=0) - self.front_center(rectangle)

