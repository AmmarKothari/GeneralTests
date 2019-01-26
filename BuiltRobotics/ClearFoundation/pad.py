import numpy as np


class Pad(object):
	def __init__(self, back_left=None, back_right=None, front_left=None, front_right=None, length=None, width=None, theta=None):
		self.bl = back_left
		self.br = back_right
		self.fr = front_right
		self.fl = front_left
		self.l = length
		self.w = width
		self.theta = theta

		if self.bl and self.br and self.l:
			self.w = np.sqrt((back_left[0] - back_right[0])**2 + (back_left[1] - back_right[1])**2)
			self.theta = np.arctan2(back_left[1] - back_right[1], back_left[0] - back_right[0])



