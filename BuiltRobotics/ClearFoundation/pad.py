import numpy as np
import pdb
import shapely.geometry as sg

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
			self.bl = np.array(self.bl)
			self.br = np.array(self.br)
			self.l = np.array(self.l)
			self.w = np.linalg.norm(self.bl - self.br)
			self.theta = np.arctan2(self.br[1] - self.bl[1], self.br[0] - self.bl[0]) - np.pi/2
			self.fl = self.bl + self.rotation(self.theta) * self.l
			self.fr = self.br + self.rotation(self.theta) * self.l

		# elif self.bl and self.fl and self.l and self.w:
		# 	self.theta = np.arctan2(self.bl)


		# if self.bl and self.br and self.l:
		# 	self.w = np.linalg.norm(np.array(back_left) - np.array(back_right))
			# self.theta = np.arctan2(back_left[1] - back_right[1], back_left[0] - back_right[0])

	@property
	def back_center(self):
		return 0.5 * (self.bl + self.br)

	@property
	def front_center(self):
		return 0.5 * (self.fl + self.fr)
	@property
	def poly(self):
		return sg.Polygon([self.bl, self.br, self.fr, self.fl])


	def rotation(self, theta):
		rot = np.array([np.cos(theta), np.sin(theta)])
		return rot



