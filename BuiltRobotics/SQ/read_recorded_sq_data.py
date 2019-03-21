

import argcomplete
import argparse
import time
import signal

import pdb

# from pybuilt.hardware.drivers.signalquest.sqgix import RawSqMsg
# msg_type = RawSqMsg

from pybuilt.hardware.drivers.signalquest.sqgix_2051 import RawSqMsg2051
msg_type = RawSqMsg2051

parser = argparse.ArgumentParser()
parser.add_argument(
        '-f', '--file', required=True)

parser.add_argument(
        '-o', '--outputfile', required=True)
		
    # -------------------------------------------------------------

argcomplete.autocomplete(parser)
args = parser.parse_args()
print 'Opening up imu recorded data: {}'.format(args.file)

with open(args.file, 'rb') as data_file:
	with open(args.outputfile, 'wb') as outputfile:
		for row in data_file:
			# msg = RawSqMsg(row.strip())
			try:
				msg = msg_type(row.strip())
				outputfile.write(msg.__repr__() + '\n')
			except:
				print('failed message')
			print msg
