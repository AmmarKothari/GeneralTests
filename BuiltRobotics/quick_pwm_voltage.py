

import os, sys
import pyperclip

idle_v = sys.argv[1]
min_v = sys.argv[2]
max_v = sys.argv[3]

analog_voltage = lambda duty: float(duty)/100.0 * 5.0

out_string = '\n\
    idle_voltage: {:0.2f}\n\
    min_voltage: {:0.2f}\n\
    max_voltage: {:0.2f}'.format(analog_voltage(idle_v), analog_voltage(min_v), analog_voltage(max_v))
    
print(out_string)
pyperclip.copy(out_string)
