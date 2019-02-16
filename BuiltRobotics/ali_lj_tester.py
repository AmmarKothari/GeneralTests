import pdb
import time

from pybuilt.hardware.drivers.labjack_ifc import LabJackInterface
from pybuilt.hardware.drivers.mcc_relay import MccRelayErb24
from pybuilt.util import helpers

SN = [470018232, 470017955]

CONNECTOR_MAP = {}

LABJACK_PORTS = [0, 2, 3, 4, 5] # DIO ports capable of PWM

MCCRELAY_PORTS = [0, 1, 2, 3, 4, 5, 6, 7, 8]

# serial number, lj_port, mcc_port
# CONTROL_MAP = [0, 0, 1] # bucket
# CONTROL_MAP = [0, 2, 2] #boom
# CONTROL_MAP = [0, 3, 3] #cab
# CONTROL_MAP = [0, 4, 4] #stick
CONTROL_MAP = [0, 5, 5] #nothing
# CONTROL_MAP = [1, 0, 5]

DUTY_CYCLE = 60.0
SLEEP_TIME = 2
helpers.init_node('Testing')

lj_sn_i = CONTROL_MAP[0]
lj_port = CONTROL_MAP[1]
mcc_port = CONTROL_MAP[2]

lj_zero = []
for lj_i, sn in enumerate(SN):
    lj_zero.append(LabJackInterface('T7', 0, 'USB', identifier=sn))
    lj_zero[i].setup_pwm_clock0()
    for lj_zero_ports in [0,2,3,4,5]:
        dio_port = 'DIO{}'.format(lj_zero_ports)
        print('Writing Port {} to Duty Cycle {}'.format(dio_port, 50.0))
        lj_zero[i].setup_pwm()
        lj_zero[i].write_pwm(dio_port, 50.0)

lj = lj_zero[lj_sn_i]
dio_port = 'DIO{}'.format(lj_port)
print('Setting up: {}'.format(dio_port))
lj.setup_pwm(dio_port)



mcc = MccRelayErb24()
mcc.open()
# sets all labjack outputs to 50% duty cycle


dio_port = 'DIO{}'.format(lj_port)
print('Writing Port {} to Duty Cycle {}'.format(dio_port, DUTY_CYCLE))
# lj.write_pwm(dio_port, DUTY_CYCLE)

for i in range(1,9):
    print('Opening relay {}'.format(i))
    mcc.set_relay(i,1)

    time.sleep(SLEEP_TIME)
    mcc.set_relay(mcc_port,0)

lj.write_pwm(dio_port, 50.0)
[mcc.set_relay(i, 0) for i in range(1,9)]
# for dio in LABJACK_PORTS:
#     dio_port = 'DIO{}'.format(dio)
#     duty_cycle = 50
#     print('Writing Port {} to Duty Cycle {}'.format(dio_port, duty_cycle))
#     lj.write_pwm(dio_port, duty_cycle)
#     time.sleep(5)

    # dio_port = 'FIO{}'.format(dio)
    # print('Setting Port {} to High'.format(dio_port))
    # lj.write_gpio(dio_port, 1)
    # time.sleep(5)
    # print('Setting Port {} to Low'.format(dio_port))
    # lj.write_gpio(dio_port, 0)

mcc.close()

lj.close()
