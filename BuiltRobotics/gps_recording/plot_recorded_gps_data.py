import argparse
import csv
import io
import os
import numpy as np
import matplotlib.pyplot as plt
import itertools
import pdb

from pybuilt.hardware.gps.nmea.nmea_ggk import GGK_TYPE_QUALITY_DESCRIPTIONS, GpsQualityTypes

ELEVATION_KEY = 'Elev'
ElEVATION_SIGMA_KEY = 'ElevSigma'
TIME_KEY = 'Time'
FIX_KEY = 'Fix'

DATA_FREQUENCY = int(10)
SMOOTHING_POINTS = int(10000)
SIGMA_LIMIT = 0.05
PLOT_FOLLOWING_TIME = 60.0/3600.0 # hours


def get_data_from_csv(csv_path):
    with io.open(os.path.expanduser(csv_path), 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        header = next(csv_reader)
        elev_index = header.index(ELEVATION_KEY)
        elev_sigma_index = header.index(ElEVATION_SIGMA_KEY)
        time_index = header.index(TIME_KEY)
        fix_index = header.index(FIX_KEY)
        elev_data = []
        for line in csv_reader:
            # Todo check if it has fix and maybe color differently? or just remove?
            if line[fix_index] == GGK_TYPE_QUALITY_DESCRIPTIONS[GpsQualityTypes.RTK_FIX]:
                elev_data.append(np.array([line[time_index], line[elev_index], line[elev_sigma_index]]).astype('float'))
    elev_data = np.array(elev_data)
    # have time start at 0 and in hours
    elev_data[:, 0] = (elev_data[:, 0] - min(elev_data[:, 0])) / 3600
    return elev_data


def log_stats(elev_data):
    total_time_h = (elev_data[-1, 0] - elev_data[0, 0])
    min_max_z = max(elev_data[:, 1]) - min(elev_data[:, 1])

    average_sigma = np.mean(elev_data[:, 2])
    max_sigma = max(elev_data[:, 2])
    min_sigma = min(elev_data[:, 2])

    percentiles = np.percentile(elev_data[:, 1], [5, 50, 95, 2.5, 97.5, 1, 99])
    print('Average Elevation: {:.3f}'.format(percentiles[0]))
    print('90% range: {:.3f} cm'.format(percentiles[2] - percentiles[1]))
    print('95% range: {:.3f} cm'.format(percentiles[4] - percentiles[3]))
    print('99% range: {:.3f} cm'.format(percentiles[6] - percentiles[5]))
    print('Total Points: {}'.format(elev_data.shape[0]))
    print('Total time: {:.3f} h, Min Max Z: {:.3f}'.format(total_time_h, min_max_z))
    print('Max Sigma: {:.3f}, Min Sigma: {:.3f}, Average Sigma: {:.3f}'.format(max_sigma, min_sigma, average_sigma))


def plot_elevation_data(elev_data):
    sampled_data = elev_data[::DATA_FREQUENCY, :]
    time_data = sampled_data[:, 0]

    plt.subplot(3, 1, 1)
    plt.plot(time_data, sampled_data[:, 1], '-')
    smoothed = convolve(elev_data[:, 1])
    plt.plot(elev_data[SMOOTHING_POINTS - 1:, 0], smoothed, 'r')
    
    plt.title('Elevation Data')
    plt.xlabel('Hours')
    plt.ylabel('Meters')
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(time_data, elev_data[:, 2][::DATA_FREQUENCY], '-')
    plt.ylim(0, 0.05)
    plt.title('Elevation Sigma')
    plt.xlabel('Hours')
    plt.ylabel('Meters')
    plt.grid(True)

    plt.subplot(3, 1, 3)
    BINS = 300
    plt.hist(elev_data[:, 1], bins=BINS)
    plt.title('PDF of Elevation ({} Bins)'.format(BINS))
    plt.xlabel('Elevation (m)')
    plt.ylabel('Count')
    plt.grid(True)


def convolve(data):
    return np.convolve(data, np.ones((SMOOTHING_POINTS,)) / SMOOTHING_POINTS, mode='valid')

def position_estimate_after_high_sigma(elev_data):
    EXAMPLES_TO_PLOT = 3
    idx_start_search = 0
    color_cycle = itertools.cycle('rgb')
    sigmas_to_check = [0.025, 0.05, 0.075]
    for sigma_limit in sigmas_to_check:
        color = next(color_cycle)
        examples = 0
        while idx_start_search < elev_data.shape[0]:
            idxs_high_sigma = np.where(elev_data[idx_start_search:, 2] > sigma_limit)[0]
            idxs_high_sigma += idx_start_search
            start_time = elev_data[idxs_high_sigma[0], 0]
            idxs = np.where((start_time < elev_data[:, 0]) & (elev_data[:, 0] < (start_time + PLOT_FOLLOWING_TIME)))[0]
            max_z = max(elev_data[idxs, 1])
            min_z = min(elev_data[idxs, 1])
            avg_sigma = np.mean(elev_data[idxs, 2])
            plt.plot(elev_data[idxs, 0] - elev_data[idxs[0], 0], elev_data[idxs, 1], color, label='{:.3f}/{:.3f}'.format(sigma_limit, avg_sigma))
            print('Min to Max: {:.3f}, Max Reading: {:.3f}, Min Reading: {:.3f}, Avg Sigma: {:.3f}'.format(max_z - min_z, max_z, min_z, avg_sigma))
            idx_start_search = idxs[-1] + 1
            examples += 1
            if examples >= EXAMPLES_TO_PLOT:
                break

    # plt.title('Z Position after a initial point with Sigma > {:.3f}'.format(SIGMA_LIMIT))
    plt.xlabel('Time (hours)')
    plt.ylabel('Z position (m)')
    plt.legend()
    plt.show()
        
    pdb.set_trace()
    


def plot_local_sigma_issues(elev_data):
    sampled_data = elev_data[::DATA_FREQUENCY, :]
    time_data = sampled_data[:, 0]

    high_sigma = []
    low_sigma = []
    for p in sampled_data:
        if p[2] > SIGMA_LIMIT:
            high_sigma.append(p)
        else:
            low_sigma.append(p)
    high_sigma = np.array(high_sigma)
    low_sigma = np.array(low_sigma)

    plt.subplot(2, 1, 1)
    plt.plot(high_sigma[:, 0], high_sigma[:, 1], 'o')
    # plt.plot(low_sigma[:, 0], low_sigma[:, 1], 'o')
    # smoothed = convolve(elev_data[:, 1])
    # plt.plot(elev_data[SMOOTHING_POINTS - 1:, 0], smoothed, 'r')
    plt.title('Elevation Data')
    plt.xlabel('Hours')
    plt.ylabel('Meters')
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(time_data, elev_data[:, 2][::DATA_FREQUENCY], '-')

    plt.title('Elevation Sigma')
    plt.xlabel('Hours')
    plt.ylabel('Meters')
    plt.grid(True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input_path', type=str, help='Path to recorded data in csv format', required=True)
    parser.add_argument('--sigma', help='Flag to plot local sigma variations', action='store_true')

    args = parser.parse_args()
    print('Starting loading data')
    # elev_data = get_data_from_csv(args.input_path)
    elev_data = np.load('/home/ammar/Desktop/elev_data.npy')
    print('Finished loading data')
    if args.sigma:
        position_estimate_after_high_sigma(elev_data)
        plot_local_sigma_issues(elev_data)
    else:
        plot_elevation_data(elev_data)
        log_stats(elev_data)
    plt.show()


if __name__ == '__main__':
    main()
