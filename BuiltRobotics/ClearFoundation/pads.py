import matplotlib.pyplot as plt
import pdb

class Pads(object):
	def __init__(self):
		self.pads_list = []

	def append(self, pad):
		self.pads_list.append(pad)

	def __getitem__(self, key):
		return self.pads_list[key]

	def __iter__(self):
		return iter(self.pads_list)

	def __len__(self):
		return len(self.pads_list)

	def draw(self, ax1 = None):
		for pad in self.pads_list:
			x,y = pad.poly.exterior.xy
			plt.plot(x,y, 'x-')