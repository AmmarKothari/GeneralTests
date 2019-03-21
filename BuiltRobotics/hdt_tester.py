from pybuilt.hardware.drivers.trimble.trimble_tcp_ifc import TrimbleTcpInterface
from pybuilt.hardware.gps.built_localization_message import BuiltLocalizationMessage, NMEA_SENTENCES
from pybuilt.hardware.gps.nmea.nmea_sentence import split_nmea_sentences, NmeaSentence
from pybuilt.hardware.gps.nmea.nmea_hdt import NmeaHDT
import pdb
import time

IP = '10.70.0.203'
PORT = 28001
TEST_TIME = 5

bx = TrimbleTcpInterface('10.70.0.203', 28001)
bx.start()
built_gps_message = BuiltLocalizationMessage()
time.sleep(0.5)
start_time = time.time()
while time.time() - start_time < TEST_TIME:
	msg = bx.next_msg()
	nmea_sentences, leftover = split_nmea_sentences(msg)
	for sent in nmea_sentences:
		if 'HDT' in sent:
			NmeaHDT()
	pdb.set_trace()




bx.stop()