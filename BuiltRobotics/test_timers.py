
from pybuilt.util.timing.timer import Timer

import time


tester = Timer(1.0, periodic = False)
tester.start()

start = time.time()
while True:
	if tester.is_ready():
		end = time.time() - start
		print ("\rElapsed Time: {}".format(end))
		tester.reset()
	else:
		print("\r Time Elapsed within Timer: {}".format(tester.elapsed())),
	