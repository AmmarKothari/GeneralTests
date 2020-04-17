import matplotlib.pyplot as plt
import click
import numpy as np

from shapely import geometry as sg

from pybuilt.util.maps import bmap
from pybuilt.geom import bpolygon

@click.group()
def cli():
    pass


@cli.command()
def map_with_obstacle():
    resolution = 1.0
    bounds = ((0.0, 0.0), (100.0, 100.0))
    test_map = bmap.BMap()
    test_map.setup_map(resolution, np.float32, bounds)
    upper_triangle = bpolygon.BPolygon(sg.Polygon([(0.0, 0.0), (99.9, 99.1), (99.9, 0.0)]))
    test_map.add_polygons([upper_triangle], value=255)
    plot_map_and_poly(test_map.cells, upper_triangle, resolution)


def plot_map_and_poly(map, poly, resolution):
    extent = [0, map.shape[0], 0, map.shape[1]]
    plt.imshow(map, origin='lower', extent=extent)
    plt.colorbar()

    y, x = poly.shapely_polygon.exterior.xy
    x = np.array(x) / resolution
    y = np.array(y) / resolution
    plt.plot(x, y, 'rx-')
    plt.xlabel('x')
    plt.ylabel('y')
    ax = plt.gca()
    # Manually draw grid lines
    for x_i in range(map.shape[0]):
        ax.axvline(x_i, ymin=0, ymax=map.shape[1])
    for y_i in range(map.shape[1]):
        ax.axhline(y_i, xmin=0, xmax=map.shape[0])
    ax.set_xlim(98, 102)
    ax.set_ylim(98, 102)
    plt.show()


if __name__ == '__main__':
    cli()
