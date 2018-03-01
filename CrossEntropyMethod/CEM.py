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


# def CEM(N, m):



# goal distribution
mu_g = 3
std_g = 1

# sampling
possible_range = (0,10)
mu_s = sum(possible_range)/2
std_s = 1
iterations = 100
samples_iter = 50
keep_samples = 5

colors = itertools.cycle(['g', 'b', 'r', 'y'])

for i in range(iterations):
	# assume a normal distribution - so sample accordingly
	samples = np.random.normal(mu_s, std_s, samples_iter)
	sample_vals = trueVal1D(samples)
	plt.hist(samples, color=next(colors))
	best_samples = samples[np.argsort(sample_vals)[-keep_samples:]]
	mu_s = np.mean(best_samples)
	std_s = np.std(best_samples)
	print('New Estimate: %s +/- %s' %(mu_s, std_s))
	if std_s < 0.1:
		std_s = 0.1
plt.show()

