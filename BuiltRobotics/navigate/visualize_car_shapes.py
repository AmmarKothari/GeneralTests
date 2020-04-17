import click
import matplotlib.pyplot as plt
import numpy as np
from shapely import affinity as sa, ops as so, geometry as sg

from pybuilt.planning.util import car_shapes, obstacle_map as obstacle_map_module
from pybuilt.test.test_tools import mocks
from pybuilt.vehicle_clients import vehicle_client


MOCKUP_PARAM_DICT = {
    'vehicle_client_key': 'excavator',
    'vehicle_name': 'ali',
    'asset_tmp_dir': '/built_tmp/',
    '/base_link_to_track_edge_y_offset': 1.72,
    '/car_shapes/angle_regions': 48,
    '/car_shapes/large/padding': 0.5,
    '/car_shapes/regular/padding': 0.0,
    'one_track_width': 0.85,
    'track_front_base_link_x_offset': 2.52,
    'track_rear_base_link_x_offset': -2.52,
    'obstacle_map_resolution': 0.3,
    'car_shapes': {
        'dummy1': 0.0,
        'dummy2': 1.0,
    },
    '/car_shapes/types': ['large', 'regular'],
    'large': {
        'padding': 0.5,
    },
    'regular': {
        'padding': 0.0,
    },
    'geofence_file': '/asset/jobs/testyard/geofence/testyard_geofence.csv'
}


@click.group()
def cli():
    click.echo('Hello World!')


@cli.command()
@click.argument('car_shapes_location')
def plot_all_car_shapes(car_shapes_location):
    """Plot all versions of the car shapes."""
    raw_car_shapes = np.load(car_shapes_location)
    car_shapes = {name: raw_car_shapes[name] for name in raw_car_shapes.files}
    for k, v in car_shapes.items():
        f, axs = plt.subplots(6, 8)
        i = 0
        for plot_row in range(6):
            for plot_col in range(8):
                axs[plot_row, plot_col].imshow(v[i], extent=[0, v[i].shape[0], 0, v[i].shape[1]], origin='lower')
                # Thsi is confusing but this is how it is!
                axs[plot_row, plot_col].set_xlabel('y axis')
                axs[plot_row, plot_col].set_ylabel('x axis')
                i += 1
    plt.show()


@cli.command()
@mocks.mock_params(MOCKUP_PARAM_DICT)
def plot_one_car_shape_with_multiple_polys():
    vehicle = vehicle_client.VehicleFactory.get_vehicle()
    obstacle_map = obstacle_map_module.ObstacleMap()
    large_car_shape = vehicle.car_shape()['large']

    base_poly = vehicle.footprint(vehicle_client.FOOTPRINT_TRACKS_BOUNDED).shapely_polygon
    x, y = sa.rotate(base_poly, -2 * np.pi / 48.0 / 2.0 + np.pi/2, use_radians=True, origin=sg.Point((0,0))).exterior.xy
    x = np.array(x) / obstacle_map.resolution + large_car_shape[0].shape[0] / 2.0
    y = np.array(y) / obstacle_map.resolution + large_car_shape[0].shape[1] / 2.0

    regular_car_shape_poly = sa.rotate(vehicle.get_car_shape_polygons()['regular'], np.pi / 2, use_radians=True)
    regular_combined_poly = _generate_all_valid_position_poly(regular_car_shape_poly, obstacle_map.resolution)
    x_regular, y_regular = regular_combined_poly.exterior.xy
    x_regular = np.array(x_regular) / obstacle_map.resolution + large_car_shape[0].shape[0] / 2.0
    y_regular = np.array(y_regular) / obstacle_map.resolution + large_car_shape[0].shape[1] / 2.0

    large_car_shape_poly = sa.rotate(vehicle.get_car_shape_polygons()['large'], np.pi / 2, use_radians=True)
    combined_poly = _generate_all_valid_position_poly(large_car_shape_poly, obstacle_map.resolution)
    x_buffered, y_buffered = combined_poly.exterior.xy
    x_buffered = np.array(x_buffered) / obstacle_map.resolution + large_car_shape[0].shape[0] / 2.0
    y_buffered = np.array(y_buffered) / obstacle_map.resolution + large_car_shape[0].shape[1] / 2.0

    plt.plot(x, y, 'bo-')
    plt.imshow(large_car_shape[0], origin='lower', extent=[0, large_car_shape[0].shape[0], 0, large_car_shape[0].shape[1]])
    plt.plot(x_buffered, y_buffered, 'r-')
    plt.plot(x_regular, y_regular, 'b:')

    # Manually draw grid lines
    ax = plt.gca()
    for x_i in range(large_car_shape[0].shape[0]):
        ax.axvline(x_i, ymin=0, ymax=large_car_shape[0].shape[0])
    for y_i in range(large_car_shape[0].shape[1]):
        ax.axhline(y_i, xmin=0, xmax=large_car_shape[0].shape[1])

    plt.show()


def _generate_all_valid_position_poly(nominal_poly, resolution):
    all_polys = []
    for x_offset in np.linspace(-0.5 * resolution, 0.5 * resolution, 5):
        for y_offset in np.linspace(-0.5 * resolution, 0.5 * resolution, 5):
            for rotation in np.linspace(0, 2 * np.pi / 48 - 0.001, 10):
                rotated_poly = sa.rotate(nominal_poly, -rotation, use_radians=True)
                translated_poly = sa.translate(rotated_poly, xoff=x_offset, yoff=y_offset)
                all_polys.append(translated_poly)
    return so.cascaded_union(all_polys)


if __name__ == "__main__":
    cli()




