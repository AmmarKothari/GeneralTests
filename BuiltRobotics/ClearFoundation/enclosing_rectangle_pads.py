from ammar_super import AmmarSuper
from constants import FOUNDATION_DIAMETER
import numpy as np
from foundation import foundation
from bcolors import bcolors
from pad import Pad
from pads import Pads
from grade_area_ABC import grade_area_ABC
import shapely.geometry as sg
import pdb

DEBUG = True

class enclosing_rectangle_pads(grade_area_ABC):
	"""Generates a set of polygons that enclose the coverage area"""
	def __init__(self, grading_poly):
		self.grading_poly = grading_poly

	def gen_foundation_pads(self):
		x_rect, y_rect = self.grading_poly.minimum_rotated_rectangle.exterior.xy
		bl_idx = 2
		bl = np.array([x_rect[bl_idx], y_rect[bl_idx]])
		br = np.array([x_rect[bl_idx-1], y_rect[bl_idx-1]])
		length = np.linalg.norm(bl - br)
		pad = Pad(back_left = bl, back_right = br, length=length)
		self.pads = Pads()
		self.pads.append(pad)
		return self.pads

	def draw(self, ax1 = None):
		x_rect, y_rect = self.grading_poly.minimum_rotated_rectangle.exterior.xy
		if not ax1:
			fig1, ax1 = plt.subplots()
		ax1.plot(x_rect, y_rect, 'r*-')

	def poly(self):
		return self.grading_poly
			

	##################
	# Helper Methods
	##################

	def debug_print(self, arg):
		return
		super().debug_print(DEBUG, arg)

if __name__ == '__main__':
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	f1.draw(ax1)
	erp = enclosing_rectangle_pads(f1.poly)
	erp.draw(ax1)
	simple_pads = erp.gen_foundation_pads()
	simple_pads.draw(ax1)
	plt.show()
	pdb.set_trace()





