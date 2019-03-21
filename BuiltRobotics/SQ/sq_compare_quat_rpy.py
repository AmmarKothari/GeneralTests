

import argcomplete
import argparse
import time
import signal
import numpy as np
import matplotlib.pyplot as plt
import pdb
from pybuilt.util.bpose import BPose
import struct

from pybuilt.hardware.drivers.signalquest.sqgix_2098 import RawSqMsg2098
msg_type = RawSqMsg2098

parser = argparse.ArgumentParser()
parser.add_argument(
        '-f', '--file', required=True)
		
    # -------------------------------------------------------------

argcomplete.autocomplete(parser)
args = parser.parse_args()
print 'Opening up imu recorded data: {}'.format(args.file)
quat = []
with open(args.file, 'rb') as data_file:
	rpy_data = []
	quat_data = []
	for row in data_file:
		try:
			msg = msg_type(row.strip())
			rpy = BPose(rpy = msg.angs)
			quat = BPose(quat_xyzw = msg.quat)
			# pdb.set_trace()
			rpy_data.append(rpy.get_rpy())
			quat_data.append(quat.get_rpy())
			print_str = ''
			for poses in (rpy, quat):
				for val in rpy.get_rpy():
					print_str += '{:.4f}, '.format(val)
				print_str += '\t'
			print(print_str)
		except struct.error:
			pass

rpy_data = np.array(rpy_data)
quat_data = np.array(quat_data)
f, axs = plt.subplots(3,1)
for r in range(3):
	for data,label in zip((rpy_data, quat_data), ('rpy', 'quat')):
		axs[r].plot(data[:, r], 'x', label=label)
	axs[r].set_ylim([-np.pi, np.pi])
axs[0].set_title(args.file)
plt.legend()
plt.show()

# pdb.set_trace()