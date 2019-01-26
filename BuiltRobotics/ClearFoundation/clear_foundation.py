from dozer_model import dozer
from matplotlib import pyplot as plt
from foundation import foundation
import time
import numpy as np

FOUNDATION_DIAMETER = 64*12*2.54 # foundation diameter at bottom in cm

morty = dozer()
f1 = foundation(FOUNDATION_DIAMETER/2)


fig1, ax1 = plt.subplots()
# ax1.grid(color='k', linestyle='-', linewidth=1)
plt.axis('equal')
plt.ylim(-FOUNDATION_DIAMETER/2, FOUNDATION_DIAMETER/2)
plt.xlim(-FOUNDATION_DIAMETER/2, FOUNDATION_DIAMETER/2)


morty.draw(ax1)
f1.draw(ax1)
# f1.circle_grid(100, np.pi/4, ax1)
f1.hex_grid(1,10,ax1)
path = [ (0,0,0), (100, 0,0), (200, 0,0)]
for p in path:
	morty.update_location(p)
	# print(morty.q)
	morty.update(ax1)
	plt.pause(2)


plt.pause(5)