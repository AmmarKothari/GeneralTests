import argparse
import csv
import io
import time

from pybuilt import spatial_reference_system
from pybuilt.hardware.drivers.trimble import trimble_tcp_ifc
from pybuilt.hardware.ifc import trimble_gps
from pybuilt.hardware.gps import gps_message
import os

import pdb

from pybuilt.util import paths
from pybuilt.util.timing import timer

local_spatial_reference_system_path = paths.get_built_pkg_path() + '/param/jobs/hq/spatial_reference_system.yaml'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', type=str, help='IP of rover', required=True)
    parser.add_argument('--port', type=int, help='Port of rover', required=True)
    parser.add_argument(
        '--output',
        type=str,
        help='Output csv file of location',
        required=False,
        default=os.path.expanduser('~/Desktop/rover.csv'))
    parser.add_argument(
        '--append',
        help='Flag to appending to file instead of overwritting',
        required=False,
        default=False,
        action="store_true")

    args = parser.parse_args()

    if not args.append:
        with io.open(args.output, 'wb') as csvfile:
            try:
                csv_writer = csv.writer(csvfile, delimiter=',')
            except ValueError as e:
                print('There was an error: {}'.format(e))

            csv_writer.writerow([
                'Time', 'Fix', 'Age of Corrections', 'Number of Satellites', 'East', 'Nort', 'Elev', 'EastSigma',
                'NorthSigma', 'ElevSigma', 'VelX', 'VelY'
            ])

    rover = trimble_gps.TrimbleGps(trimble_tcp_ifc.TrimbleTcpInterface(args.ip, args.port), gps_type_has_heading=False)
    rover.start()

    local_srs = spatial_reference_system.LocalSRS.from_yaml(local_spatial_reference_system_path)
    log_timer = timer.Timer(1.0).start()
    prev_gps_msg = None
    try:
        while True:
            msg = rover.cur_msg
            if msg:
                gps_msg = gps_message.from_nmea_msgs_with_true_heading('0', msg, local_srs)
                if prev_gps_msg and prev_gps_msg.ts == gps_msg.ts:  # same message as last time
                    continue
                values = gps_msg.ts, gps_msg.quality_type_str, gps_msg.age_of_corrections, gps_msg.num_satellites_used_in_fix,\
                     gps_msg.xyz[0], gps_msg.xyz[1], gps_msg.xyz[2], \
                     gps_msg.xyz_std_dev[0], gps_msg.xyz_std_dev[1], gps_msg.xyz_std_dev[2], \
                     gps_msg.vel_xy[0], gps_msg.vel_xy[1]
                with io.open(args.output, 'ab+') as csvfile:
                    csv_writer = csv.writer(csvfile, delimiter=',')
                    csv_writer.writerow(values)
                if log_timer.is_finished():
                    info_str = 'Time-{}, Fix-{}, Age_Of_Corrections-{:.6f}, Num_Sats: {}, XYZ-{:.6f}, {:.6f}, {:.6f}, XYZ_STDEV-{:.6f}, {:.6f}, {:.6f}, VEL_XY-{:.6f}, {:.6f}'.format(
                        *values)
                    print(info_str)
                    log_timer.start()
                prev_gps_msg = gps_msg

            time.sleep(0.001)
    except KeyboardInterrupt:
        pass
    finally:
        print('Shutting down 2')
        rover.stop()


if __name__ == '__main__':
    main()
