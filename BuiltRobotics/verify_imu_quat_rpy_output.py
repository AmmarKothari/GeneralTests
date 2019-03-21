import argparse
import signal

import argcomplete
from pybuilt.hardware.drivers.signalquest.sqgix_2098 import SqgixInterface2098
from pybuilt.util.bpose import BPose

if __name__ == '__main__':
    running = True

    parser = argparse.ArgumentParser()

    # -------------------------------------------------------------
    # Arguments
    # -------------------------------------------------------------

    parser.add_argument('-i', '--interface', metavar='interface', required=True, help='Interface to listen for data on')

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    imu = SqgixInterface2098(args.interface)

    imu.start()

    def cleanup(a, b):
        global running
        running = False

    signal.signal(signal.SIGINT, cleanup)

    try:
        last_ts = 0
        while running:
            data = imu.get_sq_data()
            if data:
                last_msg = data[-1]
                if not last_msg.is_valid():
                    print 'Invalid data, raw bytes:{}'.format(last_msg.data_bytes)
                if last_msg.ts != last_ts:
                    rpy = BPose(rpy=last_msg.angs)
                    quat = BPose(quat_xyzw=last_msg.quat)
                    print_str = ''
                    for vals in (last_msg.angs, last_msg.quat):
                        for v in vals:
                            print_str += '{:.4f}, '.format(v)
                        print_str += '\t'
                    print(print_str)
                last_ts = last_msg.ts

    except KeyboardInterrupt:
        imu.stop()
