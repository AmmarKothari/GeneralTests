import matplotlib.pyplot as plt
import numpy as np
import pdb

TRIANGLE_LEN = 300 # cm
BLADE_WIDTH = 200 # cm

class dozer():
	def __init__(self):
		self.q = [0, 0, 0]
		self.qd = [0, 0, 0]
		self.L = 1
		self.r = 0.1
		self.body = None
		self.blade = None

	def update_location(self, q):
		self.q = q

	def step(self, u, dt):
		self.qd[0] = self.r * u[0] * np.cos(self.q[2])
		self.qd[1] = self.r * u[0] * np.sin(self.q[2])
		self.qd[2] = self.r/self.L * u[1]

		self.q += qd*dt

	def draw(self, ax):
		# if self.body:

		tl = [TRIANGLE_LEN * np.cos(self.q[2]), TRIANGLE_LEN * np.sin(self.q[2])]
		self.body = ax.arrow(self.q[0]-tl[0],
			self.q[1]-tl[1],
			tl[0],
			tl[1])
		blade_ang = self.q[2] + np.pi/2
		self.blade = ax.plot(
			[self.q[0] - BLADE_WIDTH/2*np.cos(blade_ang),
			self.q[0] + BLADE_WIDTH/2*np.cos(blade_ang)],
			[self.q[1] - BLADE_WIDTH/2*np.sin(blade_ang),
			self.q[1] + BLADE_WIDTH/2*np.sin(blade_ang)],
			'rx-'
			)

	def draw_clear(self):
		if self.body:
			self.body.remove()
		if self.blade:
			self.blade.pop(0).remove()

	def update(self, ax):
		self.draw_clear()
		self.draw(ax)

