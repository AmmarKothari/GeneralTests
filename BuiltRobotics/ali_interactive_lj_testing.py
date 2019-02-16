import pdb
import time

from labjack.ljm import ljm

from pybuilt.hardware.drivers.labjack_ifc import LabJackInterface
from pybuilt.hardware.drivers.mcc_relay import MccRelayErb24
from pybuilt.util import helpers



##################
# meant to be used with python -i to debug signals
####################


SN = [470018232, 470017955]

CONNECTOR_MAP = {}

LABJACK_PORTS = [0, 2, 3, 4, 5] # DIO ports capable of PWM

MCCRELAY_PORTS = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# serial number, lj_port, mcc_port
# CONTROL_MAP = [0, 0, 1] # bucket
# CONTROL_MAP = [0, 2, 2] #boom
# CONTROL_MAP = [0, 3, 3] #cab
# CONTROL_MAP = [0, 4, 4] #stick
# CONTROL_MAP = [1, 5, 5] #nothing
# CONTROL_MAP = [1, 0, 6]

DUTY_CYCLE = 20.0
SLEEP_TIME = 5
helpers.init_node('Testing')

# lj_sn_i = CONTROL_MAP[0]
# lj_port = CONTROL_MAP[1]
# mcc_port = CONTROL_MAP[2]

lj0 = LabJackInterface('T7', 0, 'USB', identifier=SN[0])
lj1 = LabJackInterface('T7', 0, 'USB', identifier=SN[1])

lj0.open()
lj1.open()

lj0.setup_pwm_clock0()
lj1.setup_pwm_clock0()
print('lj0')
lj0.print_info()
print('lj1')
lj1.print_info()


mcc = MccRelayErb24()
mcc.open()

# dio_port = 'DIO{}'.format(lj_port)
# print('{} Setting up: {}'.format(SN[lj_sn_i], dio_port))
# lj.setup_pwm(dio_port)





# dio_port = 'DIO{}'.format(lj_port)
# print('Writing Port {} to Duty Cycle {}'.format(dio_port, DUTY_CYCLE))
# lj.write_pwm(dio_port, DUTY_CYCLE)


# print('Opening relay {}'.format(mcc_port))
# mcc.set_relay(mcc_port,1)

# time.sleep(SLEEP_TIME)
# mcc.set_relay(mcc_port,0)
# time.sleep(0.1)

# lj.write_pwm(dio_port, 50.0)
# time.sleep(0.1)

# mcc.close()
# lj.close()
