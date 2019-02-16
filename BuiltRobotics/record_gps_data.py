import sys, os
import time
import socket
import pdb
import csv



TEST_TIME = 10*60 # 10 minutes
HOSTNAME = '192.168.0.223'
PORT = 28001


gps_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
gps_socket.connect( (HOSTNAME, PORT))

save_file = 'mask_20.txt'

# checks if file exixts
if os.path.isfile(save_file):
	print('File already exists!')
	raise ValueError

with open(save_file, 'a') as csv_file:
	csv_writer = csv.writer(csv_file, delimiter='\t')
	start_time = time.time()
	while time.time() - start_time < TEST_TIME:
		raw_msg = gps_socket.recv(1000)
		msg = raw_msg.split('$PTNL')[-1] # only keep the last message
		print(msg)
		if msg:
			csv_writer.writerow([time.time(), msg])

gps_socket.shutdown(socket.SHUT_WR)