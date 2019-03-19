from constants import FOUNDATION_DIAMETER
from foundation import foundation
import numpy as np
from pad import Pad
from pads import Pads
from grade_area_ABC import grade_area_ABC
import shapely.geometry as sg
import pdb

DEBUG = True

class optimize_foundation_pads(grade_area_ABC):
	def __init__(self, grading_poly):
		super(optimize_foundation_pads, self).__init__(grading_poly)

	def gen_foundation_pads(self, *args, **kwargs):
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
		pass

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
	ofp = optimize_foundation_pads(f1.poly)
	simple_pads = ofp.gen_foundation_pads()
	simple_pads.draw(ax1)
	plt.show()
	pdb.set_trace()





