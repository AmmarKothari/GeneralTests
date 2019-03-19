import numpy as np
from scipy.optimize import minimize

from lane import lane
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, IDEAL_PUSH_DIST
from tmap import tmap
import copy

import pdb

NUM_OF_GUESSES = 10
GUESSES_TO_KEEP = 5
NOISE = 0.99
ITERATION_LIMIT = 1000
COST_STALE_LIMIT = 10
COST_STALE_THRESH = 0.1
THREAD_COUNT = 6

NUM_STARTING_POINTS_SCALE = 2

"""Incorporates optimization schemes for finding push start points for a lane"""
class lane_optimizer(lane):
	def __init__(self):
		super(lane_optimizer, self).__init__()
		# self.cost_function = self.evaluate_guess_spacing
		self.cost_function = self.evaluate_guess_tmap
		self.initial_guess_func = self.generate_evenly_spaced_start_points

	def generate_random_start_points(self):
		max_start_points = self._get_max_start_points()
		return self.length * np.sort(np.random.rand(max_start_points))

	def generate_evenly_spaced_start_points(self):
		max_start_points = self._get_max_start_points()
		return np.linspace(0, self.length, max_start_points)

	def add_noise_to_guess(self, guess, noise):
		guess += np.random.randn(len(guess)) * noise
		return np.sort(guess)

	def evaluate_guess_spacing(self, start_points):
		"""Get a lower score for evenly spacing pushes and minimizing the total number of unique points.  Penalty for not ending and starting on the pad"""
		dist_between_points = np.diff(start_points)
		dist_between_points = dist_between_points[dist_between_points>0.1] # extra points for minimizing start points
		start_and_end_correct = np.linalg.norm([start_points[0] - 0, start_points[-1] - self.length])
		difference_from_ideal = self.ideal_push_count() - dist_between_points
		return np.dot(difference_from_ideal, difference_from_ideal.T) + 10*start_and_end_correct

	def evaluate_guess_tmap(self, points):
		tmap_cost = 0
		evaluate_map = copy.deepcopy(self.tmap.map)
		idxs_to_update = self.get_idxs_with_push(points)
		
		evaluate_map = self.tmap.update_idxs_with_val(evaluate_map, np.unique(np.array(idxs_to_update), axis=0), 0.0)
		
		tmap_cost = np.sum(np.dot(evaluate_map, evaluate_map.T))
		start_and_end_correct = np.linalg.norm([points[0] - 0, points[-1] - self.length])
		dist_between_points = np.diff(points)
		dist_between_points = dist_between_points[dist_between_points>0.1] # extra points for minimizing start points
		minimizing_points_cost = 100 * len(dist_between_points)
		cost = tmap_cost + start_and_end_correct + minimizing_points_cost
		return cost

	def evaluate_guesses(self, guesses):
		return [self.cost_function(guess) for guess in guesses]

	def get_idxs_with_push(self, points):
		idxs_to_update = []
		for i in range(0,len(points)-1):
			# get all the idxs to update
			# VERTICAL POINTS -- NEED BETTER GUESSES!
			start_pt = [VPAT_WIDTH/2, points[i]]
			end_pt = [VPAT_WIDTH/2, points[i+1]]

			step_size = self.tmap.resolution*0.75
			dist = np.linalg.norm(np.array(start_pt) - np.array(end_pt))
			full_clear_dist = VPAT_CAPACITY / (self.tmap.width * self.tmap.depth ) # distance that can be cleared with VPAT
			theta_start_end = np.arctan2(end_pt[1] - start_pt[1], end_pt[0] - start_pt[0])
			# decrease all points by some amount
			if full_clear_dist > dist:
				max_capacity_pt = end_pt
			elif full_clear_dist < dist:
				max_capacity_pt = np.array(start_pt) + full_clear_dist * np.array([np.cos(theta_start_end), np.sin(theta_start_end)])
				if not self.tmap.is_valid_pt(max_capacity_pt):
					max_capacity_pt = self.tmap.get_border_pt(start_pt, end_pt)
				max_capacity_idx = self.tmap.get_tmap_idx_from_pt(max_capacity_pt)
			# print("Start: {}, End: {}".format(start_pt, max_capacity_pt))
			dist_xy = np.array(max_capacity_pt) - np.array(start_pt)
			num_of_steps = np.max(dist_xy) / self.tmap.resolution
			for path_step in np.arange(num_of_steps):
				cur_pt = start_pt + float(path_step) / num_of_steps * dist_xy
				theta_blade = np.pi/2 + theta_start_end
				blade_end_1 = cur_pt + VPAT_WIDTH/2 * np.array([np.cos(theta_blade), np.sin(theta_blade)])
				blade_end_2 = cur_pt + VPAT_WIDTH/2 * np.array([np.cos(theta_blade+np.pi), np.sin(theta_blade+np.pi)])
				blade_steps = VPAT_WIDTH/step_size
				for blade_step in np.arange(blade_steps):
					blade_pt = blade_end_1 + float(blade_step)/blade_steps * (blade_end_2 - blade_end_1)
					x_idx, y_idx = self.tmap.get_tmap_idx_from_pt(blade_pt)
					idxs_to_update.append([x_idx, y_idx])
		return idxs_to_update

	def ideal_push_count(self):
		return self.length * PAD_DEPTH * VPAT_WIDTH / VPAT_CAPACITY

	def ideal_solution(self):
		return np.arange(0, self.length, self.ideal_push_count())

	def plot_guesses(self, guesses):
		plot_array = []
		for i, guess in enumerate(guesses):
			for val in guess:
				plot_array.append([i,val])
		plot_array = np.array(plot_array)
		self.plot_pad()
		plt.plot(plot_array[:,0], plot_array[:,1], 'rx')
		plt.draw()
		plt.pause(0.000001)


	def hill_climb(self, draw=False):

		guesses = [self.initial_guess_func() for _ in range(NUM_OF_GUESSES)]
		if draw:
			plt.ion()
			f1, ax1 = plt.subplots(1)
			self.plot_guesses(guesses)

		costs = self.evaluate_guesses(guesses)
		cost_stale_counter = 0
		iteration = 0
		while np.min(costs) > 1.0 and iteration < ITERATION_LIMIT and cost_stale_counter < COST_STALE_LIMIT:
			keep_guesses = []
			for idx in np.argsort(costs).astype(int)[0:GUESSES_TO_KEEP]:
				keep_guesses.append(guesses[idx])
			for i in range(0, GUESSES_TO_KEEP):
				# guess_to_perturb_idx = np.random.randint(GUESSES_TO_KEEP)
				guess_to_perturb_idx = i
				guess_to_perturb = copy.deepcopy(keep_guesses[guess_to_perturb_idx])
				keep_guesses.append(self.add_noise_to_guess(guess_to_perturb, NOISE*np.exp(-iteration/100)))
			guesses = np.sort(np.array(copy.deepcopy(keep_guesses)), axis=1)
			new_costs = self.evaluate_guesses(guesses)
			if abs(np.min(costs) - np.min(new_costs)) < COST_STALE_THRESH:
				cost_stale_counter += 1
			if draw:
				plt.cla()
				self.plot_guesses(guesses)


			iteration += 1
			print('Iteration {}, Best Cost: {:.4f}'.format(iteration, np.min(costs)))

		print('Best Guess: {}, with score {}'.format(guesses[np.argmin(costs)], np.min(costs)))
		print('Ideal Solution: {}'.format(self.ideal_solution()))
		if draw:
			plt.plot(np.zeros(len(self.ideal_solution())), self.ideal_solution(), 'bo')
			idxs = self.get_idxs_with_push(guesses[np.argmin(costs)])
			updated_tmap = self.tmap.update_idxs_with_val(self.tmap.map, idxs, 0.0)
			self.tmap.set_map(updated_tmap)
			self.tmap.plot_tmap()
			plt.pause(0)



	#################
	# Helper Methods
	#################
	def _get_max_start_points(self):
		return np.ceil(NUM_STARTING_POINTS_SCALE * self.length / self.ideal_push_count()).astype('int')


if __name__ == '__main__':
	l = lane_optimizer()
	l.create_pad(10, PAD_DEPTH)
	l.hill_climb(draw=True)











			# assuming all in a vertical line for now
			# threads = []
			# manager = multiprocessing.Manager()
			# return_dict = manager.dict()
			# for thread in range(THREAD_COUNT):
			# 	p = multiprocessing.Process(target=self.tmap.update_tmap_with_push_multiprocess,
			# 		args=([self.width/2, start_points[i]],
			# 			[self.width/2, start_points[i+1]],
			# 			None,
			# 			thread,
			# 			return_dict))
			# 	p.start()
			# 	threads.append(p)

			# for thread in threads:
			# 	thread.join()

