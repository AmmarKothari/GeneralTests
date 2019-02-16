import socket
import time
import pdb


TCP_IP = '192.168.0.160'
TCP_PORT = 23
BUFFER_SIZE = 1024

MESSAGES = ('STOP', 'PAUSE', 'LINK', 'TXSTATUS', 'WATCHDOG')

# socket.setblocking(False)
socket.setdefaulttimeout(0.1)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

start_time = time.time()
TIME_TO_RUN = 1
while time.time() - start_time < TIME_TO_RUN:
	response = ''
	for msg in MESSAGES:
		try:
			s.send('{}\r\n'.format(msg))
			data = s.recv(BUFFER_SIZE)
			# print('{}: Data Received: {}'.format(msg, data))
			response += data
		except:
			print('Error {}'.format(msg))
			break
	print(response.replace('\n', '\t').replace('\r', ''))

s.close()