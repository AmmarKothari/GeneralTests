from ammar_super import AmmarSuper
from constants import FOUNDATION_DIAMETER
import numpy as np
from foundation import foundation
from bcolors import bcolors
from pad import Pad
from pads import Pads
from grade_area_ABC import grade_area_ABC
import shapely.geometry as sg
import pdb

DEBUG = True

class enclosing_polygon_pads(grade_area_ABC):
	"""Generates a set of polygons that enclose the coverage area"""
	def __init__(self, grading_poly):
		super(enclosing_polygon_pads, self).__init__(grading_poly)
		self.estimate_radius(self.grading_poly)

	def estimate_radius(self, grading_poly):
		"""estimates the radius of a circle that encloses grading polygon area"""
		xy = np.array([(x,y) for x,y in zip(*grading_poly.exterior.xy)])
		center_pt = np.mean(xy, axis=0)
		max_diff = np.max(xy - center_pt, axis=0)
		self.radius = np.linalg.norm(max_diff)


	def gen_foundation_pads(self, polygon_sides):
		self.polygon_sides = polygon_sides
		polygon_props = self.get_polygon_props(polygon_sides)
		xy_vertices = self.circumscribed_polygon_points(polygon_props['sides'])
		total_points = len(xy_vertices)
		# choose vertice with smallest x component as bl of first rectangle
		first_pt_idx = np.argmin(np.array(xy_vertices)[:, 1])
		# only need to add 1 when its odd
		last_pt_idx = 1 + first_pt_idx + \
			abs(first_pt_idx - np.argmax(np.array(xy_vertices)
										 [:, 1]))  # br of last rectangle
		self.debug_print('{}, {}'.format(first_pt_idx, last_pt_idx))
		self.pads = Pads()
		for i in range(first_pt_idx, last_pt_idx):
			i_cur = i % total_points
			i_next = (i + 1) % total_points
			sub_pad = Pad(back_left=xy_vertices[i_cur], back_right=xy_vertices[
						  i_next], length=polygon_props['length'])
			self.pads.append(sub_pad)
		return self.pads

	def draw(self, ax1 = None):
		if not self.polygon_sides:
			print('Polygon Sides not set')
			raise ValueError
		if not ax1:
			fig1, ax1 = plt.subplots()
		polygon_props = self.get_polygon_props(self.polygon_sides)
		xy_vertices = self.circumscribed_polygon_points(polygon_props['sides'])
		self.draw_polygon(xy_vertices, ax1)

	def poly(self):
		return self.grading_poly

	@property
	def polygon_sides(self):
		return self._polygon_sides

	@polygon_sides.setter
	def polygon_sides(self, polygon_sides):
		if self.check_polygon(polygon_sides):
			self._polygon_sides = polygon_sides
			

	##################
	# Helper Methods
	##################

	def debug_print(self, arg):
		return
		super().debug_print(DEBUG, arg)

	def get_radius(self):
		x_rect, y_rect = self.grading_poly.minimum_rotated_rectangle.exterior.xy
		x_cent = np.mean(x_rect)
		y_cent = np.mean(y_rect)
		self.radius = np.linalg.norm([x_rect - x_cent, y_rect - y_cent])

	def check_polygon(self, polygon_sides):
		if int(polygon_sides) % 2 != 1:
			print(bcolors.FAIL + 'Polygon must have odd number of sides' + bcolors.ENDC)
			return False
		return True

	def get_polygon_props(self, polygon_sides):
		width = 2 * self.radius * np.tan(0.5 * 2 * np.pi / polygon_sides)
		length = 2 * self.polygon_radius(polygon_sides)
		polygon_props = {'sides': polygon_sides,
						 'width': width, 'length': length}
		return polygon_props

	def circumscribed_polygon_points(self, polygon_sides):
		xy = []
		angle = self.polygon_angle(polygon_sides)
		dist_to_vertex = self.polygon_radius(polygon_sides)
		for i in range(polygon_sides):
			xy.append(
				[dist_to_vertex * np.sin(np.pi * 2 * (float(i)) / polygon_sides),
				 dist_to_vertex * np.cos(np.pi * 2 * (float(i)) / polygon_sides)]
			)
		return xy

	def polygon_side_length(self, polygon_sides):
		angle = self.polygon_angle(polygon_sides)
		dist_to_vertex = self.radius / np.cos(angle)
		side_length = 2 * np.sqrt(dist_to_vertex**2 - self.radius ** 2)
		return side_length

	def polygon_radius(self, polygon_sides):
		# distance from vertex to center
		angle = self.polygon_angle(polygon_sides)
		return self.radius / np.cos(angle)

	def polygon_angle(self, polygon_sides):
		return np.pi / polygon_sides

	def draw_polygon(self, points, ax):
		# draw a polygon from points
		x, y = sg.Polygon(points).exterior.xy
		plt.plot(x, y, alpha=0.2, linewidth=3, color='k')

if __name__ == '__main__':
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	f1.draw(ax1)
	epp = enclosing_polygon_pads(f1.radius, f1.poly)
	epp.polygon_sides = 7
	epp.draw(ax1)
	simple_pads = epp.gen_foundation_pads(7)
	simple_pads.draw(ax1)
	plt.show()
	pdb.set_trace()





