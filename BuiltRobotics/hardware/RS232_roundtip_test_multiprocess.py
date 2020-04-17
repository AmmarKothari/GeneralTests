import time
from multiprocessing import Process, Queue, Value, Event
import pdb
import numpy as np




TOTAL_TEST_TIME = 100 # seconds
SLEEP_TIME_BETWEEN_SENDS = 0.01

time_sent = list()
time_received = list()

# USBID_1 = 1
# USBID_2 = 3
# ser_write_file = '/dev/ttyUSB{}'.format(USBID_1)
# ser_read_file =  '/dev/ttyUSB{}'.format(USBID_2)

USBID_1 = 1
USBID_2 = 2
ser_write_file = '/dev/ttyS{}'.format(USBID_1)
ser_read_file =  '/dev/ttyS{}'.format(USBID_2)

def write_serial(q, do_run):
	print('Starting write process: {}'.format(ser_write_file))
	idx = 0
	with open(ser_write_file, 'a', buffering=0) as write_file:
		while not do_run.is_set():
			send_time = time.time()
			write_file.write('{}, {:.10f}\n'.format(idx, send_time))
			q.put('{}, {:.10f}\n'.format(idx, send_time))
			idx += 1
			time.sleep(SLEEP_TIME_BETWEEN_SENDS)
	print('Closing write file')
	print('Stopping write thread')

def read_serial(q, do_run):
	print('Starting read process: {}'.format(ser_read_file))
	out = ''
	with open(ser_read_file, 'r') as read_file:
		while not do_run.is_set():
			out += read_file.readline()
			if '\n' in out:
				msgs = out.split('\n')
				if msgs[-1].count(',') < 2:
					out = msgs.pop() #keeps last message in read queue
				else:
					out = ''
				for msg in msgs:
					receive_time = msg
					q.put([msg, time.time()])
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



q_read = Queue()
q_write = Queue()
do_run_read = Event()
do_run_write = Event()

p_write = Process(target = write_serial, args = (q_write, do_run_write))
p_read = Process(target = read_serial, args = (q_read, do_run_read))

p_read.start()
p_write.start()

end_time = time.time() + TOTAL_TEST_TIME
time.sleep(TOTAL_TEST_TIME)

print('Starting end Processes')
do_run_write.set()
time.sleep(1.0)
do_run_read.set()
time.sleep(1.0)

print('Complete end Processes')

while not q_write.empty():
	msg = q_write.get()
	time_sent.append(msg)

while not q_read.empty():
	msg = q_read.get()
	time_received.append(msg[0].strip() + ', {:.10f}\n'.format(msg[1]))

if p_write.is_alive():
	p_write.terminate()
if p_read.is_alive():
	p_read.terminate()


print("Messages Sent: {} \t Messages Received: {}".format(len(time_sent), len(time_received)))

if len(time_received) < 1:
	print('No messages received!')
else:
	try:
		time_received_array = convert_strings_to_arrays(time_received)
	except:
		pdb.set_trace()
	time_diff = time_received_array[:,2] - time_received_array[:,1]
	time_diff_mean = np.mean(time_diff)
	time_diff_std = np.std(time_diff)

	print('Test Time: {} s'.format(TOTAL_TEST_TIME))
	print('Average Latency: {} +/- {} seconds'.format(time_diff_mean, time_diff_std))
	print('Max Time: {} | Min Time: {}'.format(np.max(time_diff), np.min(time_diff)))
	mean_packet_size = np.mean(np.array([np.array(t).itemsize for t in time_sent]))
	print('Mean Packet Size: {:.2f} bytes'.format(mean_packet_size))

pdb.set_trace()



