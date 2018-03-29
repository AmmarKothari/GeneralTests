import numpy as np
import matplotlib.pyplot as plt


final_timesteps = 60*60.0
pretrain_labels = 10
final_labels = 100
current_label = 0


def exp_desired_labels(timesteps_elapsed):
	global current_label
	"""Return the number of labels desired at this point in training. """
	exp_decay_frac = 0.01 ** (timesteps_elapsed / final_timesteps)  # Decay from 1 to 0
	pretrain_frac = pretrain_labels / final_labels
	desired_frac = pretrain_frac + (1 - pretrain_frac) * (1 - exp_decay_frac)  # Start with 0.25 and anneal to 0.99
	if current_label < int(desired_frac * final_labels):
		current_label = desired_frac * final_labels
		return current_label
	else:
		return 0

# def const_desired_labels(timesteps_elapsed):
	# return pretrain_labels + (timesteps_elapsed - self._started_at) / self._seconds_between_labels



label = [exp_desired_labels(t) for t in np.arange(final_timesteps)]

plt.plot(np.arange(final_timesteps), label, 'rx')
plt.show()

