import can
from pybuilt.hardware.retrofit.single_message_payload_checker import generate_message_from_defls
import time
import pdb
from multiprocessing import Queue, Process


class Timer(object):
	def __init__(self, time):
		self.time_to_wait = time
		self.start_time = 0

	def start(self):
		self.start_time = time.time()

	def expired(self):
		elapsed = time.time() - self.start_time
		if elapsed > self.time_to_wait:
			return True
		return False

	def restart(self):
		self.start()
	



SEND_BUS_ID = 'vcan0'
RECV_BUS_ID = 'vcan1'

FREQ = 10
SEND_TIME = 0.1
def send_msg(q, send_bus, default_msg):
	do_run = True
	default_timer = Timer(10*SEND_TIME)
	periodic_sender = send_bus.send_periodic(default_msg, 1.0/FREQ, 0.1)
	period_timer = Timer(SEND_TIME)
	while do_run:
		if default_timer.expired():
			msg = default_msg
			default_timer.restart()
		else:
			if not q.empty():
				msg = q.get(False) # non-blocking
				if msg == 'q': # put a zero when ready to end
					do_run = False
					continue
				default_timer.restart()
		periodic_sender.modify_data(msg)
		if period_timer.expired():
			periodic_sender.start()
			period_timer.restart()
	print('stopping send')


SEND_FREQ = 100
TIME_TO_SEND = 5.0

send_bus = can.interface.Bus(SEND_BUS_ID, bustype='socketcan_ctypes')
recv_bus = can.interface.Bus(RECV_BUS_ID, bustype='socketcan_ctypes')

zero_msg = generate_message_from_defls([0,0]).can_msg

q_send_msgs = Queue()
p_send = Process(target = send_msg, args=(q_send_msgs, send_bus, zero_msg))

p_send.start()
# q_send_msgs.put(msg, send_bus, zero_msg)


while True:
	defl = raw_input('Desired Deflection: ')
	# pdb.set_trace()
	if defl == 'q':
		q_send_msgs.put(defl)
		break
	try:
		defl = int(defl)
	except:
		continue
	# for i in range(100000):
	# 	defl = i%1000
	q_send_msgs.put(generate_message_from_defls([defl,0]).can_msg)

p_send.join(1.0)

print('Finished')





# send_periodic_task = send_bus.send_periodic(, 1.0 / SEND_FREQ, 0.01)
# send_periodic_task.start()

# # time.sleep(TIME_TO_SEND/2.0)
# for i in range(0,1023):
# 	send_periodic_task.modify_data(generate_message_from_defls([i,0]).can_msg)
# 	send_periodic_task.start()
# 	# pdb.set_trace()
# 	time.sleep(0.01)
# # print('modified send data')
# time.sleep(TIME_TO_SEND/2.0 + 0.5)

# pdb.set_trace()

# print('Finished')