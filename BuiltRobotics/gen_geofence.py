#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import csv

import argparse
import datetime
import shapely.geometry as sg
from shapely.ops import cascaded_union
import numpy as np

from pybuilt.util.action.parsers import csv_file_to_linear_surfaces
from pybuilt.util.helpers import get_built_pkg_path

DEFAULT_END_PAD_BUFFER_DIST = 12
DEFAULT_SIDE_PAD_BUFFER_DIST = 2

DEFAULT_PADS_CSV = '/asset/jobs/{job}/pads/pads.csv'
GEOFENCE_FOLDER = '/asset/jobs/{job}/geofence/'


def get_xyzs_geofence(pads_in_geofence, end_buffer, side_buffer):
    bpolys = []
    for surface in pads_in_geofence:
        surface = surface['surface']
        # Extend the ends and increment the width to get an outer edge
        surface = surface.extend_front(end_buffer).extend_back(end_buffer).extend_left_side(
            side_buffer).extend_right_side(side_buffer)
        bpolys.append(surface.bpolygon)
    poly = cascaded_union([bpoly.get_shapely_polygon() for bpoly in bpolys])
    if isinstance(poly, sg.Polygon):
        return list(poly.exterior.coords)
    elif isinstance(poly, sg.MultiPolygon):
        return poly.convex_hull.exterior.coords


def build_filename(job, surfaces):
    geofence_fname = ''
    for pad in [pad_surface['pad'] for pad_surface in surfaces]:
        geofence_fname += '{}_'.format(pad)
    geofence_fname += datetime.datetime.now().strftime("%Y_%m_%d") + '.csv'
    geofence_fname = GEOFENCE_FOLDER.format(job=job) + geofence_fname

    return geofence_fname


def generate_geofence_from_args(args):
    """Generate the geofence from a set of arguments.

    :param args:  (argparse.ArgumentParser) args for geofence
    :return:
    """

    # end_buffer = float(args.end_buffer) if args.end_buffer else DEFAULT_END_PAD_BUFFER_DIST
    # side_buffer = float(args.side_buffer) if args.side_buffer else DEFAULT_SIDE_PAD_BUFFER_DIST

    pads_surfaces = csv_file_to_linear_surfaces(args.input)
    pads_surfaces = [pad_surface for pad_surface in pads_surfaces if pad_surface['pad'] in args.pads]

    fname = build_filename(args.job, pads_surfaces)
    geofence_xyzs = get_xyzs_geofence(pads_surfaces, args.end_buffer, args.side_buffer)
    print("Center of Geofence: {}".format(np.array(geofence_xyzs).mean(axis=0)))

    with open(get_built_pkg_path() + fname, 'w+') as csvfile:
        writer = csv.writer(csvfile)
        for x, y, z in geofence_xyzs:
            writer.writerow([float(x), float(y), float(z)])

    print 'Generated pads from file: {}\npads loaded={}\n'.format(args.input,
                                                                  [pad_surface['pad'] for pad_surface in pads_surfaces])

    print '{}.yaml:\n\n' \
          'pads_file: {} # (remove everything up to asset!!)\n' \
          'geofence_file: {}\n' \
          'terrain_map_coords_file: {}'\
        .format(args.job, args.input, fname, fname)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j', '--job', help='Job to generate geofence for', required=True)
    parser.add_argument('-i', '--input', help='Input CSV to generate geofence from', required=True)
    parser.add_argument(
        '-e',
        '--end_buffer',
        default=DEFAULT_END_PAD_BUFFER_DIST,
        help='End buffer distance for end of pad (default={})'.format(DEFAULT_END_PAD_BUFFER_DIST))
    parser.add_argument(
        '-s',
        '--side_buffer',
        default=DEFAULT_SIDE_PAD_BUFFER_DIST,
        help='Side buffer distance for end of pad (default={})'.format(DEFAULT_SIDE_PAD_BUFFER_DIST))
    parser.add_argument('pads', nargs='+', help='Pads to build the geofence for')
    parser.add_argument(
        '-uy',
        '--update_yaml',
        help='Update system.yaml with new geofence',
        required=False,
        default=False,
        action='store_true')
    parser.add_argument(
        '-ub',
        '--update_blaunch',
        help='Update ri_sim.blaunch with new geofence',
        required=False,
        default=False,
        action='store_true')
    args = parser.parse_args()

    generate_geofence_from_args(args)
