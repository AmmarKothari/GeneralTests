import time
import threading
import pdb
import numpy as np
import os
from pybuilt.hardware.drivers.serial_reader import SerialReader
USBID_1 = 1
USBID_2 = 2
# USBID_2 = 3

TOTAL_TEST_TIME = 100 # seconds
SLEEP_TIME_BETWEEN_SENDS = 0.01

time_sent = list()
time_received = list()

def convert_strings_to_arrays(string_array):
	data = list()
	for s in string_array:
		s_split = s.strip().split(',')
		data.append([int(s_split[0]), float(s_split[1]), float(s_split[2])])
	return np.array(data)


# ser_write_file = '/dev/ttyUSB{}'.format(USBID_1)
# ser_read_file =  '/dev/ttyUSB{}'.format(USBID_2)
ser_write_file = '/dev/ttyS{}'.format(USBID_1)
ser_read_file =  '/dev/ttyS{}'.format(USBID_2)


end_time = time.time() + TOTAL_TEST_TIME

with open(ser_read_file, 'r') as read_file:
	with open(ser_write_file, 'a', buffering=0) as write_file:
		idx = 0
		out = ''
		while time.time() < end_time:
			# write message
			send_msg = '{}, {:.10f}\n'.format(idx, time.time())
			write_file.write(send_msg)
			idx += 1
			# wait for message to come through
			out += read_file.readline()
			if '\n' in out:
				msgs = out.split('\n')
				if msgs[-1].count(',') < 2:
					out = msgs.pop() #keeps last message in read queue
				else:
					out = ''
				for msg in msgs:
					sent_time = msg
					time_received.append(sent_time.strip() + ', {:.10f}\n'.format(time.time()))
			elif len(out) > 100:
				print('uhoh Current Data: {}'.format(out))
				out = ''
			time_sent.append(send_msg)

print("Messages Sent: {} \t Messages Received: {}".format(len(time_sent), len(time_received)))

if len(time_received) < 1:
	print('No messages received!')
else:

	time_received_array = convert_strings_to_arrays(time_received)
	time_diff = time_received_array[:,2] - time_received_array[:,1]
	time_diff_mean = np.mean(time_diff)
	time_diff_std = np.std(time_diff)

	print('Test Time: {} s'.format(TOTAL_TEST_TIME))
	print('Average Latency: {} +/- {} seconds'.format(time_diff_mean, time_diff_std))
	print('Max Time: {} | Min Time: {}'.format(np.max(time_diff), np.min(time_diff)))
	mean_packet_size = np.mean(np.array([np.array(t).itemsize for t in time_sent]))
	print('Mean Packet Size: {:.2f} bytes'.format(mean_packet_size))





