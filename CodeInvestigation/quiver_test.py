import numpy as np
import matplotlib.pyplot as plt
import pdb
import copy

ax = plt.subplot(1,1,1)

R = np.arange(-10,10,1.0)
X,Y = np.meshgrid(R, R)
U = copy.deepcopy(X)
V = copy.deepcopy(Y)

for ix,x in enumerate(R):
	for iy,y in enumerate(R):
		U[ix, iy] = 1
		V[ix, iy] = 1
Q = ax.quiver(X, Y, U, V, units='width')
plt.show()