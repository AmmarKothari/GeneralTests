import pdb
import time

from pybuilt.hardware.drivers.mcc_relay import MccRelayErb24

mcc = MccRelayErb24()
mcc.open()
mcc.blink_led()

mcc.set_relay(9, 1)

time.sleep(5.0)

mcc.set_relay(9, 0)

mcc.close()