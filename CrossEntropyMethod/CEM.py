import numpy as np
import scipy.stats
import pdb
import matplotlib.pyplot as plt
import itertools



# useful if you can evaluate each sample independently
# figure out how this relates to KL divergence?
# # the subsequent mean and std must be similar to the previous mean and std

def trueVal1D(v):
	# return scipy.stats.norm.cdf(v) - scipy.stats.norm.cdf(0)
	norm_samples = (v - mu_g)/std_g
	return -abs(scipy.stats.norm.cdf(norm_samples) - 0.5)

def pickBest(vals, keep):
	return samples[np.argsort(vals)[-keep:]]


# def CEM(N, m):



# goal distribution
mu_g = 3
std_g = 1

# sampling
possible_range = (0,10)
mu_s = sum(possible_range)/2
std_s = 1
iterations = 100
samples_iter = 10
keep_samples = 5

colors = itertools.cycle(['g', 'b', 'r', 'y'])

for i in range(iterations):
	# assume a normal distribution - so sample accordingly
	samples = np.random.normal(mu_s, std_s, samples_iter)
	sample_vals = trueVal1D(samples)
	plt.hist(samples, color=next(colors))
	# do importance sampling
	samples_scaled = (sample_vals-np.min(sample_vals))/(np.max(sample_vals)-np.min(sample_vals))
	samples_norm = samples_scaled/np.sum(samples_scaled)
	samples_norm_sum = np.cumsum(samples_norm)
	# pdb.set_trace()
	keepers = []
	for s in np.random.rand(keep_samples):
		idx = np.abs(samples_norm_sum - s).argmin()
		if s > samples_norm_sum[idx]:
			idx += 1
		try:
			keepers.append(samples[idx])
		except:
			pdb.set_trace()
	# best_samples = pickBest(samples, keep_samples)
	# mu_s = np.mean(best_samples)
	# std_s = np.std(best_samples)

	mu_s = np.mean(keepers)
	std_s = np.std(keepers)

	print('New Estimate: %s +/- %s' %(mu_s, std_s))
	# if std_s < 0.1:
	# 	std_s = 0.1
plt.show()

