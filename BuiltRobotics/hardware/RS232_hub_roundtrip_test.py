import time
import threading
import pdb
import numpy as np
import os
from pybuilt.hardware.drivers.serial_reader import SerialReader
USBID_1 = 1
USBID_2 = 3

TOTAL_TEST_TIME = 100 # seconds
SLEEP_TIME_BETWEEN_SENDS = 0.01

time_sent = list()
time_received = list()

def write_serial():
	print('Starting write thread: {}'.format(ser_write_file))
	t = threading.currentThread()
	idx = 0
	with open(ser_write_file, 'a', buffering=0) as write_file:
		while getattr(t, "do_run", True):
			send_time = time.time()
			write_file.write('{}, {:.10f}\n'.format(idx, send_time))
			time_sent.append('{}, {:.10f}\n'.format(idx, send_time))
			idx += 1
			time.sleep(SLEEP_TIME_BETWEEN_SENDS)
	print('Closing write file')
	print('Stopping write thread')
	return

def read_serial():
	print('Starting read thread: {}'.format(ser_read_file))
	t = threading.currentThread()
	out = ''
	with open(ser_read_file, 'r') as read_file:
		while getattr(t, "do_run", True):
			out += read_file.read()
			if '\n' in out:
				msgs = out.split('\n')
				if msgs[-1].count(',') < 2:
					out = msgs.pop() #keeps last message in read queue
				else:
					out = ''
				for msg in msgs:
					receive_time = msg
					time_received.append(receive_time.strip() + ', {:.10f}\n'.format(time.time()))
			elif len(out) > 100:
				print('uhoh Current Data: {}'.format(out))
				out = ''
	print('Closing read file')
	print('Stopping read thread')


def convert_strings_to_arrays(string_array):
	data = list()
	for s in string_array:
		s_split = s.strip().split(',')
		data.append([int(s_split[0]), float(s_split[1]), float(s_split[2])])
	return np.array(data)


ser_write_file = '/dev/ttyUSB{}'.format(USBID_1)
ser_read_file =  '/dev/ttyUSB{}'.format(USBID_2)

write_thread = threading.Thread(target=write_serial)
# read_thread = threading.Thread(target=read_serial)

pdb.set_trace()
read_serial = SerialReader(ser_read_file)
read_serial.start()

# read_thread.start()
write_thread.start()

end_time = time.time() + TOTAL_TEST_TIME
while time.time() < end_time:
	msg = read_serial.next_msg()
	time_received.append(msg.strip() + ', {:.10f}\n'.format(time.time()))

print('Starting end Threads')
write_thread.do_run = False
time.sleep(0.1)
write_thread.join(0.1)
time.sleep(2.0)
# read_thread.do_run = False
# read_thread.join(0.1)
print('Complete end Threads')

# pdb.set_trace()
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


read_serial.stop()





