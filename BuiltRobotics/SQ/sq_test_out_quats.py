

import argcomplete
import argparse
import time
import signal
import numpy as np
import matplotlib.pyplot as plt
import pdb

# from pybuilt.hardware.drivers.signalquest.sqgix import RawSqMsg
# msg_type = RawSqMsg

from pybuilt.hardware.drivers.signalquest.sqgix_2098 import RawSqMsg2098
msg_type = RawSqMsg2098

parser = argparse.ArgumentParser()
parser.add_argument(
        '-f', '--file', required=True)

parser.add_argument(
        '-o', '--outputfile', required=True)
		
    # -------------------------------------------------------------

argcomplete.autocomplete(parser)
args = parser.parse_args()
print 'Opening up imu recorded data: {}'.format(args.file)
quat = []
with open(args.file, 'rb') as data_file:
	with open(args.outputfile, 'wb') as outputfile:
		for row in data_file:
			try:
				msg = msg_type(row.strip())
				outputfile.write('{:.4f}, {:.4f}, {:.4f}, {:.4f}'.format(*msg.quat) + '\n')
				quat.append(msg.quat)
				print(msg)
			except:
				print('failed message')


f, axs = plt.subplots(4,1)
quat = np.array(quat)
for i in range(4):
	axs[i].plot(quat[:, i], 'rx')
	axs[i].set_ylim([-1,1])
plt.show()