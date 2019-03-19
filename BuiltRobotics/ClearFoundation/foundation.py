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
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, FOUNDATION_DIAMETER
import scipy.optimize as sopt
from grade_area_ABC import grade_area_ABC



DEBUG = False

COST_MULTIPLIER = {'ungraded_area': 100}

class foundation(grade_area_ABC):
	MAX_NUMBER_OF_PADS = 3
	POINTS_DEFINE_PAD = 5

	def __init__(self, radius):
		self.radius = radius
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

	@property
	def poly(self):
		return self.circle


if __name__ == '__main__':
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	f1.draw(ax1)
	plt.show()
	# f1.hex_grid_one_side(11, ax1)
	# f1.optimize_hex_grid_one_side(ax1)
	# plt.show()
