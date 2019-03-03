import numpy as np


def linear_interp_between_pts(start_pt, end_pt, num_points):
	interp_points = [np.linspace(start_pt[i], end_pt[i], int(
		num_points)) for i in range(len(start_pt))]
	return np.array(interp_points).T

def get_vertice_array_from_poly(poly):
	return np.array([(x,y) for x,y in zip(*poly.exterior.xy)])