import csv
import pdb
from pybuilt.hardware.gps.nmea.nmea_pjk import NmeaPJK
import copy
import numpy as np
import matplotlib.pyplot as plt

FILENAMES = ['mask_10.txt', 'mask_15.txt', 'mask_20.txt']
data_dict = {'northing':0, 'easting': 0, 'height': 0, 'num_satellites': 0, 'dop': 100}

def plot_data(axis, time_data, data, title, mask_val):
	mean_val = np.mean(data)
	std_val = np.std(data)
	# axis.plot(time_data, data - mean_val, 'rx')

	smoothed_values = np.convolve(data, np.full(SMOOTHING_WINDOW, 1.0/SMOOTHING_WINDOW), mode='valid')
	axis.plot(time_data[SMOOTHING_WINDOW/2:-SMOOTHING_WINDOW/2+1], smoothed_values - mean_val, label='{}: {:.2f} +/- {:.2f}'.format(mask_val, np.mean(smoothed_values - mean_val), std_val))
	# axis.plot(time_data[SMOOTHING_WINDOW/2:-SMOOTHING_WINDOW/2+1], smoothed_values - mean_val)
	axis.set_title(title)


fig, axes = plt.subplots(4,1)
SMOOTHING_WINDOW = 100
assert SMOOTHING_WINDOW%2 == 0
for fn in FILENAMES:
	mask_val = fn.split('_')[1].split('.')[0]
	data_array = []
	with open(fn, 'r') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter = '\t')
		for line in csv_reader:
			pjk_dict = copy.deepcopy(data_dict)
			read_time = line[0]
			sentences = line[1]
			pjk_sentence = line[1].split('\r')[0]
			try:
				pjk = NmeaPJK(pjk_sentence, read_time)
				pjk_dict['northing'] = pjk.northing
				pjk_dict['easting'] = pjk.easting
				pjk_dict['height'] = pjk.height_antenna_phase_center
				pjk_dict['num_satellites'] = pjk.num_satellites_fixed
				pjk_dict['dop'] = pjk.dop
			except Exception as e:
				print('ERROR: {}'.format(e.message))
				print('Message: {}'.format(line))
			pjk_array = [float(read_time), pjk_dict['northing'], pjk_dict['easting'], pjk_dict['height'], pjk_dict['num_satellites']]
			if any(np.array(pjk_array) == 0):
				continue
			data_array.append(pjk_array)



	data_array = np.array(data_array).astype(float)
	data_array[:,0] = data_array[:, 0] - data_array[0,0]
	mean_values = np.mean(data_array, axis = 0)

	# Northing
	plot_data(axes[0], data_array[:,0], data_array[:,1], 'Northing', mask_val)

	# Easting
	plot_data(axes[1], data_array[:,0], data_array[:,2], 'Easting', mask_val)

	# Height
	plot_data(axes[2], data_array[:,0], data_array[:,3], 'Height', mask_val)

	# SVs
	axes[3].plot(data_array[:,0], data_array[:,4])
	axes[3].set_title('Num SVs')
# fig.suptitle(fn)
# axes[0].legend(['10', '15', '20'])
[ax.legend() for ax in axes]
[ax.set_xlim(0, 600) for ax in axes]
plt.show()