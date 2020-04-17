import pdb
import time

from labjack.ljm import ljm

from pybuilt.hardware.drivers.labjack_ifc import LabJackInterface
from pybuilt.hardware.drivers.mcc_relay import MccRelayErb24
from pybuilt.util import helpers

SN = [470018232, 470017955]

CONNECTOR_MAP = {}

LABJACK_PORTS = [0, 2, 3, 4, 5] # DIO ports capable of PWM

MCCRELAY_PORTS = [0, 1, 2, 3, 4, 5, 6, 7, 8]

lj = SN[0]
lj_port = 0
mcc_port = 0

helpers.init_node('Testing')

labjacks = ljm.listAllS('LJM_dtANY', 'LJM_ctANY')
print('Opening Labjack: {}'.format(labjacks[3]))
pdb.set_trace()
lj = LabJackInterface('T7', 0, 'USB', identifier=labjacks[3][0])

lj.open()
lj.print_info()
lj.setup_pwm_clock0()

for dio in LABJACK_PORTS:
    dio_port = 'DIO{}'.format(dio)
    print('Setting up: {}'.format(dio_port))
    lj.setup_pwm(dio_port)

# mcc = MccRelayErb24()
# mcc.open()
#
# mcc.set_relay(9, 1)

for dio in LABJACK_PORTS:
    dio_port = 'DIO{}'.format(dio)
    duty_cycle = 50
    print('Writing Port {} to Duty Cycle {}'.format(dio_port, duty_cycle))
    lj.write_pwm(dio_port, duty_cycle)
    time.sleep(5)

    # dio_port = 'FIO{}'.format(dio)
    # print('Setting Port {} to High'.format(dio_port))
    # lj.write_gpio(dio_port, 1)
    # time.sleep(5)
    # print('Setting Port {} to Low'.format(dio_port))
    # lj.write_gpio(dio_port, 0)

# mcc.close()

lj.close()
