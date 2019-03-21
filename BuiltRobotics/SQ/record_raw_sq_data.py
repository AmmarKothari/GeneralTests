
import argcomplete
import argparse
import time
import signal

# from pybuilt.hardware.drivers.signalquest.sqgix import SQGIXInterface
# sqinterface = SQGIXInterface


from pybuilt.hardware.drivers.signalquest.sqgix_2098 import SqgixInterface2098
sqinterface = SqgixInterface2098


running = True

parser = argparse.ArgumentParser()
parser.add_argument(
        '-i', '--interface', metavar='interface', required=True, help='List of nodes that will be allowed to die')
parser.add_argument(
        '-f', '--file', metavar='interface', required=True, help='List of nodes that will be allowed to die')

    # -------------------------------------------------------------

argcomplete.autocomplete(parser)
args = parser.parse_args()
print 'Opening up imu interface: {}'.format(args.interface)

imu = sqinterface(args.interface)
imu.start()


def cleanup(a, b):
    global running
    running = False

signal.signal(signal.SIGINT, cleanup)

with open(args.file, 'wb') as imu_file:

	msg_count = 0
	try:
	    last_ts = 0
	    while running:
	        data = imu.get_sq_data()
	        if data:
	            last_msg = data[-1]
	            if not last_msg.is_valid():
	                print 'Invalid data, raw bytes:{}'.format(last_msg.data_bytes)
	            if last_msg.ts != last_ts:
	            	imu_file.write(last_msg.data_bytes + '\n')
	                print last_msg.ts - last_ts, last_msg
	                msg_count += 1

	            last_ts = last_msg.ts
	except KeyboardInterrupt:
	    pass