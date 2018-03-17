import numpy as np
import scipy.stats
import pdb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import itertools



# useful if you can evaluate each sample independently
# figure out how this relates to KL divergence?
# # the subsequent mean and std must be similar to the previous mean and std

# I don't know why it can't estimate covariance

def absTrueVal(v):
	# no noise in true value
	sample_vals = -np.sum(abs(v - mu_g), 1)
	return sample_vals

def stochTrueVal(v):
	# true value comes from a distribution
	v_stoch =  np.random.multivariate_normal(mu_g, cov_g, size=v.shape[0])
	sample_vals = -np.sum(abs(v - v_stoch), 1)
	return sample_vals

# def CEM(N, m):



# goal distribution
mu_g = [30, 40]
cov_g = np.diag([1, 1])
# sampling
possible_range = (0,100)
mu_s = sum(possible_range)/2 * np.ones_like(mu_g)
cov_s = np.diag(np.ones_like(mu_s))
iterations = 100
samples_iter = 50
keep_samples = 5

colors = itertools.cycle(['g', 'b', 'r', 'y'])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for i in range(iterations):
	# assume a normal distribution - so sample accordingly
	samples = np.random.multivariate_normal(mu_s, cov_s, size=samples_iter)
	# sample_vals = absTrueVal(samples)
	sample_vals = stochTrueVal(samples)

	hist, xedges, yedges = np.histogram2d(samples[:,0], samples[:,1])
	xpos, ypos = np.meshgrid(xedges[:-1] + 0.25, yedges[:-1] + 0.25)
	xpos = xpos.flatten('F')
	ypos = ypos.flatten('F')
	zpos = np.zeros_like(xpos)
	dx = 0.5 * np.ones_like(zpos)
	dy = dx.copy()
	dz = hist.flatten()

	# ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=next(colors), zsort='average')
	best_samples = samples[np.argsort(sample_vals)[-keep_samples:], :]
	mu_s = np.mean(best_samples, axis=0)
	cov_s = np.cov(best_samples, rowvar=False)
	print('New Estimate: %s +/- %s' %(mu_s, cov_s))

	# have a check for direction.  if on one end of the range like greater than one std,
	# then increase stdev otherwise continue

	# if np.linalg.norm(cov_s) < 0.001:
	# 	cov_s = 0.1 * np.ones_like(cov_s)
# plt.show()

