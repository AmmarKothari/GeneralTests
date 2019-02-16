import yaml
import argparse
import signal
import matplotlib
import pdb
import re
import os
import math
import numpy as np

from pybuilt.hardware.drivers.sqgix import SQGIXInterface


KIN_FILE = os.path.expanduser('~/built_ws/src/built/param/vehicles/ex/cat_336/cat_336.yaml')
SQ_OFFSETS = os.path.expanduser('~/built_ws/src/built/param/vehicles/ex/cat_336/ali.yaml')
# INTERFACES = ['/dev/sqgix_cab', '/dev/sqgix_boom', '/dev/sqgix_stick', '/dev/sqgix_bucket']
INTERFACES = ['/dev/sqgix_boom', '/dev/sqgix_stick', '/dev/sqgix_bucket']

running = True

#load parameters
kin = yaml.load(open(KIN_FILE))
sq_offsets = yaml.load(open(SQ_OFFSETS))['sq_imu']['mounting_offsets']

link_keys = ['boom_length', 'stick_length', 'bucket_length']
offset_keys = ['boom', 'stick', 'bucket']

# initialize IMUs
imus = [SQGIXInterface(interface) for interface in INTERFACES]
[imu.start for imu in imus]


def cleanup(a, b):
    global running
    running = False

def eulerAnglesToRotationMatrix(theta, x) :
    # pitch, roll, yaw
    R_x = np.array([[1,         0,                  0                   ],
                    [0,         math.cos(theta[0]), -math.sin(theta[0]) ],
                    [0,         math.sin(theta[0]), math.cos(theta[0])  ]
                    ])
         
         
                     
    R_y = np.array([[math.cos(theta[1]),    0,      math.sin(theta[1])  ],
                    [0,                     1,      0                   ],
                    [-math.sin(theta[1]),   0,      math.cos(theta[1])  ]
                    ])
                 
    R_z = np.array([[math.cos(theta[2]),    -math.sin(theta[2]),    0],
                    [math.sin(theta[2]),    math.cos(theta[2]),     0],
                    [0,                     0,                      1]
                    ])
                     
                     
    R = np.dot(R_z, np.dot( R_y, R_x ))

    Tf = [
    		[R[0,0:2], x[0]],
    		[R[1,0:2], x[1]],
    		[R[2,0:2], x[2]]
    		[0,0,0, x[0]]
		]

 
    return R

signal.signal(signal.SIGINT, cleanup)

try:
    while running:
    	datas = []
    	# Rs = list()
    	pitches = dict()
    	for imu in imus:
	        data = imu.get_sq_data()
	        if len(data) > 0 and data[0].is_valid():
	            print('Bad Checksum')
	        elif data:
	        	roll_degs = re.split(',|=', data)[1]
	        	pitch_degs = re.split(',|=', data)[3]
	        	roll_rads = np.deg2rad(float(roll_degs))
	        	pitch_rads = np.deg2rad(float(pitch_degs))

	        	pitches.append(pitch_rads)
	        	datas.append(data)

	        	# pdb.set_trace()
        		# Rs.append(eulerAnglesToRotationMatrix([pitch_rads, roll_rads, 0.0], []))
		boom_effective_angle = pitches[0] + sq_offsets['boom'][0]
		boom_length = kin[link_keys[0]
		boom_end = [np.cos(boom_effective_angle) * boom_length,
					np.sin(boom_effective_angle) * boom_length,
					1]

		# start_R = np.eye(4)
		# Boom_end = start_R * Rs[1]
		# Stick_end = start_R *



	            # for d in data:
	            #     print d
except KeyboardInterrupt:
    pass
finally:
    print 'Cleaning up imu'
    imu.stop()

print 'Exiting... Goodbye'

#ImuData<roll_degs=-84.0000, pitch_degs=-0.3000, accels=[-0.0784, 9.6824, -1.0192],         self.ang_vels=[0.0017, -0.0017, 0.0122]>
