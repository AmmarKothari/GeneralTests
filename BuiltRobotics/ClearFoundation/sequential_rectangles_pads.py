from grade_area_ABC import grade_area_ABC
from constants import VPAT_WIDTH
import numpy as np
import shapely.geometry as sg
from constants import FOUNDATION_DIAMETER
from foundation import foundation
from pads import Pads
from pad import Pad
from helper_funcs import get_vertice_array_from_poly
import copy

import pdb


class sequential_rectangles_pads(grade_area_ABC):
	"""create a series of rectangles that are one blade width from one side to the other"""
	def __init__(self, grading_poly):
		super(sequential_rectangles_pads, self).__init__(grading_poly)


	def gen_foundation_pads(self, *args, **kwargs):
		xy = get_vertice_array_from_poly(self.grading_poly)
		self.pads = Pads()
		rect = {}
		rect['mid_left'] = xy[np.argmin(xy[:,0])]
		right_most_x = np.max(xy[:,0])
		lane_count = 1
		while rect['mid_left'][0] < right_most_x:
			# assumes that the orientation of the lane is in the y direction -- could use perpindicular to side of polygon
			rect['mid_right'] = rect['mid_left'] + np.array([VPAT_WIDTH, 0])
			height = self.get_pad_length(rect['mid_right'], rect['mid_left'])
			rect['height'] = height
			rect['front_right'] = rect['mid_right'] + np.array([0, height/2])
			rect['front_left'] = rect['mid_left'] + np.array([0, height/2])
			rect['back_right'] = rect['front_right'] - np.array([0, height])
			rect['back_left'] = rect['front_right'] - np.array([VPAT_WIDTH, height])
			self.pads.append(Pad(back_left = rect['back_left'], back_right = rect['back_right'], length=height))
			lane_count += 1
			rect['mid_left'] = copy.deepcopy(rect['mid_right'])
		return self.pads

	def get_pad_length(self, mid_right, mid_left):
		try:
			front_right = self.get_line_intersection_point_with_poly([mid_right, mid_right + np.array([0, 1e5])]) # some really large value
			front_left = front_right - np.array([VPAT_WIDTH, 0])
		except NotImplementedError:
			front_right = mid_right
			print('No right side intersection')
		try:
			front_left = self.get_line_intersection_point_with_poly([mid_left, mid_left + np.array([0, 1e5])]) # get left side intersection with polygon
		except NotImplementedError:
			print('No left side intersection')
		height = np.max([
			np.linalg.norm(mid_right - front_right) * 2,
			np.linalg.norm(mid_left - front_left) * 2,
			])
		return height


	def get_line_intersection_point_with_poly(self, points):
		intersection_line = self.grading_poly.intersection(sg.LineString(points))
		if len(intersection_line.xy[0]) == 1: # special case where edge intersects with poly
			intersection_point = points[0]
		else:
			intersection_point = np.array([(x,y) for x,y in zip(*intersection_line.xy)])[1,:]
		return intersection_point

	def draw(self, ax1=None):
		pass

	def poly(self):
		return self.grading_poly

	def print_pad_info(self, pad_dict):
		for i,k in pad_dict.items():
			print('{}: {}'.format(i,k))




if __name__ == '__main__':
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	f1.draw(ax1)
	srp = sequential_rectangles_pads(f1.poly)
	simple_pads = srp.gen_foundation_pads()
	simple_pads.draw(ax1)
	plt.show()

