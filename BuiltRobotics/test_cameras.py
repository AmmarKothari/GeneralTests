import cv2
import time

import pdb

DEVICE_ID = 1
DEVICE_IP = '192.168.1.20'
vid_cap = cv2.VideoCapture(DEVICE_IP)

for i in range(100):
	# pdb.set_trace()
	status, img = vid_cap.read()
	if status:
		cv2.imshow('image', img)
		cv2.waitKey(0.05)
	else:
		print('No image captured')




vid_cap.release()
