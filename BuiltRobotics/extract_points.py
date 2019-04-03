import ogr
import os
import pdb
import numpy as np
import matplotlib.pyplot as plt
from shapely import geometry as sg
from shapely import ops as so

FN = '~/Downloads/roma_east_gps/RE_A5_ROW_IFC.dbf'
MAX_DIST_BETWEEN_POINTS = 3.0

def extract_polygon_vertexes(fn):
	"""Return a dict with keys the name of each segment and the values are a list of points for that polygon"""
	path_to_infile = os.path.expanduser(FN)
	driver = ogr.GetDriverByName('ESRI Shapefile') 
	infile = driver.Open(path_to_infile) 
	layer = infile.GetLayer()
	vertex_dict = {}
	for area in layer:
		area_shape = area.GetGeometryRef() 
		area_polygon = area_shape.GetGeometryRef(0)
		no_of_polygon_vertices = area_polygon.GetPointCount()
		print("Extracting points for {}".format(area['CORRIDOR_I']))
		points = []
		for vertex in xrange(no_of_polygon_vertices): 
			lon, lat, z = area_polygon.GetPoint(vertex)
			point = (lon, lat, z)
			points.append(point)
		if area['CORRIDOR_I'] in vertex_dict.keys():
			print('Appending unique identifier to name')
			num_append = np.sum([area['CORRIDOR_I']==name for name in vertex_dict.keys()]) + 1
			area['CORRIDOR_I'] = "{}_{}".format(area['CORRIDOR_I'], num_append)
		vertex_dict[area['CORRIDOR_I']] = points
	return vertex_dict


def plot_raw_points_from_vertex_dict(vertex_dict):
	all_points = []
	for points in vertex_dict.values():
		all_points.extend(points)
	all_points = np.array(all_points)
	plt.plot(all_points[:,0], all_points[:,1], 'rx')
	plt.show()

def create_polygon(vertexes):
	containing_poly = sg.Polygon(vertexes)
	return containing_poly

def create_dense_point_polygon(vertexes):
	"""adds point if there is too large of seperation between them"""
	polygon_points = []
	for v1, v2 in zip(vertexes[0:-1], vertexes[1:]):
		polygon_points.append(v1)
		while sg.Point(polygon_points[-1]).distance(sg.Point(v2)) > MAX_DIST_BETWEEN_POINTS:
			print('Adding point -- Distance Between Points: {}'.format(sg.Point(polygon_points[-1]).distance(sg.Point(v2))))
			ls = sg.LineString((polygon_points[-1], v2))
			new_point = ls.interpolate(MAX_DIST_BETWEEN_POINTS)
			polygon_points.append(new_point.coords[0])
		polygon_points.append(v2)
	return create_polygon(polygon_points)
		

def create_row_polygon(vertex_dict):
	polygon_list = []
	for vertexes in vertex_dict.values():
		polygon = create_polygon(vertexes)
		polygon_list.append(polygon)
	return polygon_list

def remove_small_features(polygon):
	return polygon.buffer(0.1).buffer(-0.1)

def union_of_polygon_list(polygon_list):
	all_row_poly = so.cascaded_union(polygon_list)
	# return remove_small_features(all_row_poly)
	return all_row_poly

def plot_polygon(polygon):
	x,y = polygon.exterior.xy
	plt.plot(x,y, 'bo:')
	plt.show()



vertex_dict = extract_polygon_vertexes(FN)
# plot_raw_points_from_vertex_dict(vertex_dict)

polygon_list = create_row_polygon(vertex_dict)
# for poly in polygon_list:
# 	plot_polygon(poly)
row_polygon = union_of_polygon_list(polygon_list)
plot_polygon(row_polygon)

pdb.set_trace()