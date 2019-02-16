from pybuilt.hardware.drivers.sqgix import SQGIXInterface
import argparse
import signal



IMU_INTERFACE = ['sqgix_cab', 'sqgix_boom', 'sqgix_stick', 'sqgix_bucket']

running = True
imus = [SQGIXInterface('/dev/' + interface) for interface in IMU_INTERFACE]

for imu in imus:
    imu.start()


def cleanup(a, b):
    global running
    running = False


signal.signal(signal.SIGINT, cleanup)

try:
    while running:
        for id, imu in enumerate(imus):
            data = imu.get_sq_data()
            if data:
                for d in data:
                    print '{}: {}'.format(id, d)
except KeyboardInterrupt:
    pass
finally:
    print 'Cleaning up imus'
    for imu in imus:
        imu.stop()


