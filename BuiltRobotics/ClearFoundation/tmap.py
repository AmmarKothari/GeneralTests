import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pdb

from constants import IDEAL_PUSH_DIST, VPAT_CAPACITY, VPAT_WIDTH

class tmap(object):
	def __init__(self, x_start, y_start, length, width, depth, resolution):

		self.x_start = x_start
		self.y_start = y_start
		self.length = length
		self.width = width
		self.resolution = resolution
		self.depth = depth

		x_dim = int(width/resolution)
		y_dim = int(length/resolution)

		self.map = np.full( (x_dim, y_dim), depth )
		self.plot_ready = False
		self.plot = True

	def get_tmap_idx_from_pt(self, pt):
		x,y = pt
		x_idx = self._pt_to_idx_in_bounds(x, self.x_start, self.resolution, 0, self.map.shape[0]-1)
		y_idx = self._pt_to_idx_in_bounds(y, self.y_start, self.resolution, 0, self.map.shape[0]-1)
		return x_idx, y_idx

	def update_tmap_with_push(self, start_pt, end_pt, step_size=None):
		"""updates the tmap according to a push."""

		if not step_size:
			step_size = self.resolution*0.75

		dist = np.linalg.norm(np.hstack( (start_pt, end_pt) ) )
		full_clear_dist = VPAT_CAPACITY / (self.width * self.depth ) # distance that can be cleared with VPAT
		theta_start_end = np.arctan2(end_pt[1] - start_pt[1], end_pt[0] - start_pt[0])
		# decrease all points by some amount
		if full_clear_dist > dist:
			max_capacity_pt = end_pt
		elif full_clear_dist < dist:
			max_capacity_pt = np.array(start_pt) + full_clear_dist * np.array([np.cos(theta_start_end), np.sin(theta_start_end)])
			max_capacity_idx = self.get_tmap_idx_from_pt(max_capacity_pt)
		print("Start: {}, End: {}".format(start_pt, max_capacity_pt))
		dist_xy = np.array(max_capacity_pt) - np.array(start_pt)
		num_of_steps = np.max(dist_xy) / self.resolution
		for path_step in np.arange(num_of_steps):
			cur_pt = start_pt + float(path_step) / num_of_steps * (dist_xy)
			theta_blade = np.pi/2 + theta_start_end
			blade_end_1 = cur_pt + VPAT_WIDTH/2 * np.array([np.cos(theta_blade), np.sin(theta_blade)])
			blade_end_2 = cur_pt + VPAT_WIDTH/2 * np.array([np.cos(theta_blade+np.pi), np.sin(theta_blade+np.pi)])
			blade_steps = VPAT_WIDTH/step_size
			for blade_step in np.arange(blade_steps):
				blade_pt = blade_end_1 + float(blade_step)/blade_steps * (blade_end_2 - blade_end_1)
				x_idx, y_idx = self.get_tmap_idx_from_pt(blade_pt)
				self.map[x_idx,y_idx] = 0
		if self.plot:
			self.plot_tmap()
		return np.sum(np.dot(self.map, self.map.T))


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

	###############
	#  HELPER FUNCS
	###############
	def _pt_to_idx(self, val, start, resolution):
		return int( (val-start)/resolution)

	def _pt_to_idx_in_bounds(self, val, start, resolution, val_min, val_max):
		idx = self._pt_to_idx(val, start, resolution)
		return np.clip(idx, val_min, val_max)

	def _is_valid_pt(self, pt):
		"""Is it a valid point in the tmap"""
		x,y = pt
		if x < self.x_start:
			return False
		if x > (self.x_start + self.width):
			return False
		if y < self.y_start:
			return False
		if y > (self.y_start + self.length)
			return False
		return True


