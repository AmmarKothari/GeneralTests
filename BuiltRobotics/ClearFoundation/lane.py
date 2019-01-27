
from ammar_super import AmmarSuper
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, IDEAL_PUSH_DIST
from tmap import tmap

import shapely.geometry as sg
import copy

import matplotlib.pyplot as plt
import numpy as np

import multiprocessing

import pdb

DEBUG = False

HEIGHT_MAP_RESOLUTION = 0.1 # 10 cm

class lane(AmmarSuper):
	def __init__(self):
		pass

	def debug_print(self, arg):
		super().debug_print(DEBUG, arg)

	def create_pad(self, length, depth):
		# assume that the pad width is a single blade width
		BL = [0,0]
		BR = [VPAT_WIDTH, 0]
		FR = [VPAT_WIDTH, length]
		FL = [0, length]
		self.pad = sg.Polygon([BL, BR, FR, FL])
		self.length = length
		self.width = VPAT_WIDTH

		self.FC = self.front_center(self.pad)
		self.BC = self.back_center(self.pad)
		self.tmap = tmap(0,0,length, VPAT_WIDTH, depth, HEIGHT_MAP_RESOLUTION, False)

	def plot_pad(self):
		x,y = self.pad.exterior.xy
		plt.plot(x,y,'b:')

	def front_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[0:2], axis=0)

	def back_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[2:4], axis=0) - self.front_center(rectangle)






if __name__ == '__main__':
	l = lane()
	l.create_pad(10, PAD_DEPTH)
	l.plot_pad()






