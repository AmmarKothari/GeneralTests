import matplotlib.pyplot as plt
# import seaborn as sns
import numpy as np
import pdb
import copy

from constants import IDEAL_PUSH_DIST, VPAT_CAPACITY, VPAT_WIDTH

class tmap(object):
	def __init__(self, x_start, y_start, length, width, depth, resolution, showPlot=False):

		self.x_start = x_start
		self.y_start = y_start
		self.length = length
		self.width = width
		self.resolution = resolution
		self.depth = depth

		x_dim = int(width/resolution)
		y_dim = int(length/resolution)


		self.original_map = np.full( (x_dim, y_dim), depth )
		self.map = copy.deepcopy(self.original_map)
		self.plot_ready = False
		self.plot = showPlot

	def get_tmap_idx_from_pt(self, pt):
		x,y = pt
		x_idx = self._pt_to_idx_in_bounds(x, self.x_start, self.resolution, 0, self.map.shape[0]-1)
		y_idx = self._pt_to_idx_in_bounds(y, self.y_start, self.resolution, 0, self.map.shape[1]-1)
		return x_idx, y_idx

	def update_tmap_with_push_multiprocess(self, start_pt, end_pt, step_size=None, worker_num=None, return_dict=None):
		cost = self.update_tmap_with_push(start_pt, end_pt, step_size)
		print('Process {}: {}'.format(worker_num, cost))
		return_dict[worker_num] = cost
		return return_dict

	def plot_tmap(self):
		plt.ion()
		if not self.plot_ready:
			self.f1, self.a1 = plt.subplots(1,1)
		heatmap = self.a1.imshow(self.map.T, cmap='hot', interpolation='nearest')
		if not self.plot_ready:
			plt.colorbar(heatmap)
			self.plot_ready = True
			plt.xticks(np.linspace(0, self.map.shape[0], 2), np.linspace(0, self.width, 2))
			plt.yticks(np.linspace(0, self.map.shape[1], 5), np.linspace(0, self.length, 5))

		plt.draw()
		plt.pause(0.001)

	def reset(self):
		self.map = copy.deepcopy(self.original_map)

	def get_border_pt(self, pt1, pt2):
		""" only checks intersection with the top end of the map"""
		return self._get_intersect(pt1, pt2, [0, self.length], [self.width, self.length])

	@staticmethod
	def update_idxs_with_val(map, idxs, val):
		for idx in idxs:
			map[idx[0], idx[1]] = val
		return map

	def set_map(self, map):
		self.map = map


	###############
	#  HELPER FUNCS
	###############
	def _pt_to_idx(self, val, start, resolution):
		return int( (val-start)/resolution)

	def _pt_to_idx_in_bounds(self, val, start, resolution, val_min, val_max):
		idx = self._pt_to_idx(val, start, resolution)
		return np.clip(idx, val_min, val_max)

	def is_valid_pt(self, pt):
		"""Is it a valid point in the tmap"""
		x,y = pt
		if x < self.x_start:
			return False
		if x > (self.x_start + self.width):
			return False
		if y < self.y_start:
			return False
		if y > (self.y_start + self.length):
			return False
		return True

	def _get_intersect(self, a1, a2, b1, b2):
		""" 
		Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
		a1: [x, y] a point on the first line
		a2: [x, y] another point on the first line
		b1: [x, y] a point on the second line
		b2: [x, y] another point on the second line
		"""
		s = np.vstack([a1,a2,b1,b2])        # s for stacked
		h = np.hstack((s, np.ones((4, 1)))) # h for homogeneous
		l1 = np.cross(h[0], h[1])           # get first line
		l2 = np.cross(h[2], h[3])           # get second line
		x, y, z = np.cross(l1, l2)          # point of intersection
		if z == 0:                          # lines are parallel
		    return (float('inf'), float('inf'))
		return (x/z, y/z)



