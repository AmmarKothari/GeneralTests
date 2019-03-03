import serial
import subprocess
import pdb
import re
import time
import os

PORT = '/dev/cu.usbmodem1421'
SSID_INFO_CMD = '/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I'
TIME_TO_WAIT_FOR_DEVICE = 5.0
TIME_BETWEEN_READS = 0.1
DEVICE_ID_STRING = b'Computer Status Device\n'

class ComputerState(object):
	def __init__(self):
		self.ser = None

	def get_usb_port(self):
		tty_ports = os.listdir('/dev')
		for port in tty_ports:
			if 'cu.usbmodem' in port:
				print('Opening port: {}'.format(port))
				try:
					ser = serial.Serial('/dev/' + port)
					ser.close()
					ser.open()
					start_read_time = time.time()
					while time.time() - start_read_time < TIME_TO_WAIT_FOR_DEVICE:
						time.sleep(TIME_BETWEEN_READS)
						device_text = ser.readline()
						if device_text == DEVICE_ID_STRING:
							return '/dev/' + port
				except serial.SerialException as e:
					print(e)


	def open(self, port):
		self.ser = serial.Serial(port)
		self.ser.close()
		self.ser.open()

	def get_power_state(self):
		return 1

	def get_ip(self):
		scanoutput = subprocess.check_output(["ifconfig"])
		ip_start_idx = scanoutput.find(b'10.0')
		ip_end_idx = scanoutput[ip_start_idx:].find(b' ') + ip_start_idx
		return scanoutput[ip_start_idx:ip_end_idx].decode("utf-8")

	def get_ssid(self):
		process = subprocess.Popen(SSID_INFO_CMD.split(), stdout=subprocess.PIPE)
		out, err = process.communicate()
		process.wait()
		try:
			ssid = re.search(r' SSID: .*\n', out.decode('utf-8')).group(0).split(':')[-1].strip().replace(' ', '')
			return ssid
		except AttributeError:
			return 'N/A'

	def gen_computer_state(self):
		power_state = self.get_power_state()
		ip_addr = self.get_ip()
		ssid = self.get_ssid()
		state_string = 'IP: {}, SSID: {}'.format(ip_addr, ssid)
		return state_string

	def print_computer_info(self):
		print(self.gen_computer_state())


	def start_stream(self):
		self.open(CS.get_usb_port())
		try:
			while True:
				ser_string = self.gen_computer_state()
				print(ser_string)
				self.ser.write(ser_string.encode('utf-8'))
				time.sleep(5.0)

		except KeyboardInterrupt:
			print('Killed')

		self.ser.close()


if __name__ == '__main__':
	CS = ComputerState()
	CS.start_stream()