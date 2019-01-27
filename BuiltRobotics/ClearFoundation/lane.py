
from ammar_super import AmmarSuper
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, IDEAL_PUSH_DIST
from tmap import tmap

import shapely.geometry as sg
import copy

import matplotlib.pyplot as plt
import numpy as np

import pdb

DEBUG = False
NUM_OF_GUESSES = 10
GUESSES_TO_KEEP = 5
NOISE = 0.99
ITERATION_LIMIT = 1000

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
		self.tmap = tmap(0,0,length, VPAT_WIDTH, depth, HEIGHT_MAP_RESOLUTION)

		# self.cost_fuction = self.evaluate_guess
		self.cost_function = self.evaluate_guess_tmap

	def plot_pad(self):
		x,y = self.pad.exterior.xy
		plt.plot(x,y,'b:')


	def front_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[0:2], axis=0)

	def back_center(self, rectangle):
		return np.mean(np.array(rectangle.exterior.xy).T[2:4], axis=0) - self.front_center(rectangle)

	def generate_random_start_points(self):
		max_start_points = np.ceil(2 * self.length / self.ideal_push_count()).astype('int')
		return self.length * np.sort(np.random.rand(max_start_points))

	def add_noise_to_guess(self, guess, noise):
		guess += np.random.randn(len(guess)) * noise
		return np.sort(guess)

	def evaluate_guess(self, start_points):
		"""Get a lower score for evenly spacing pushes and minimizing the total number of unique points.  Penalty for not ending and starting on the pad"""
		dist_between_points = np.diff(start_points)
		dist_between_points = dist_between_points[dist_between_points>0.1] # extra points for minimizing start points
		start_and_end_correct = np.linalg.norm([start_points[0] - 0, start_points[-1] - self.length])
		difference_from_ideal = self.ideal_push_count() - dist_between_points
		return np.dot(difference_from_ideal, difference_from_ideal.T) + 10*start_and_end_correct

	def evaluate_guess_tmap(self, start_points):
		cost = 0
		pdb.set_trace()
		for i in range(0,len(start_points)-1):
			# assuming all in a vertical line for now
			cost += self.tmap.update_tmap_with_push([self.width/2, start_points[i]], [self.width/2, start_points[i+1]])
		pdb.set_trace()
		return cost

	def evaluate_guesses(self, guesses):
		print('Evaluating Guesses')
		return [self.cost_function(guess) for guess in guesses]

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

		guesses = [self.generate_random_start_points() for _ in range(NUM_OF_GUESSES)]
		if draw:
			plt.ion()
			f1, ax1 = plt.subplots(1)
			self.plot_guesses(guesses)

		costs = self.evaluate_guesses(guesses)
		iteration = 0
		while np.min(costs) > 5e-2 and iteration< ITERATION_LIMIT:
			keep_guesses = []
			# pdb.set_trace()
			for idx in np.argsort(costs)[0:GUESSES_TO_KEEP]:
				keep_guesses.append(guesses[idx])
			for i in range(0, GUESSES_TO_KEEP):
				# guess_to_perturb_idx = np.random.randint(GUESSES_TO_KEEP)
				guess_to_perturb_idx = i
				guess_to_perturb = copy.deepcopy(keep_guesses[guess_to_perturb_idx])
				keep_guesses.append(self.add_noise_to_guess(guess_to_perturb, NOISE*np.exp(-iteration/100)))
			guesses = np.sort(np.array(copy.deepcopy(keep_guesses)), axis=1)
			costs = self.evaluate_guesses(guesses)
			if draw:
				plt.cla()
				self.plot_guesses(guesses)


			iteration += 1
			print('Iteration {}, Best Cost: {:.4f}'.format(iteration, np.min(costs)))

		print('Best Guess: {}, with score {}'.format(guesses[np.argmin(costs)], np.min(costs)))
		print('Ideal Solution: {}'.format(self.ideal_solution()))
		if draw:
			plt.plot(np.zeros(len(self.ideal_solution())), self.ideal_solution(), 'bo')
			plt.pause(0)






if __name__ == '__main__':
	l = lane()
	l.create_pad(10, PAD_DEPTH)
	l.hill_climb(draw=False)






