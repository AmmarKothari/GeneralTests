import datetime

import yfinance
import numpy as np
import time

NORMAL_MEAN = 0.5
NORMAL_STD = 0.25


class LoadHistoricalData:
    def __init__(self, name):
        self.name = name
        self.ticker = yfinance.Ticker(name)
        self.data = None

    def load_data_for_date_range(self, start=None, end=None, duration=None, interval='1d'):
        if start is None and end is None:
            raise Exception('Not a valid range.  Need start or end.')
        if (start is None or end is None) and duration is None:
            raise Exception('Not a valid range. Need a duration when only providing one end of range')
        if start is not None and end is None:
            end = start + datetime.timedelta(duration)
        if start is None and end is not None:
            start = end - datetime.timedelta(duration)
        self.data = self.ticker.history(start=start, end=end, interval=interval)
        return self

    def get_price_change_data(self):
        if self.data is None:
            raise Exception('Data not loaded.')
        return (np.array(self.data['Open']) - np.array(self.data['Close'])) / np.array(self.data['Open'])

    def get_price_data(self):
        return (np.array(self.data['Close']))


class StockChangeSampler:
    def __init__(self, data, random_seed=None):
        self.data = np.sort(data)  # Data to sample for monte carlo simulation
        self.data_points = len(data)
        self.random = np.random.RandomState(random_seed)

    def get_uniform_val(self, num_vals=1):
        return self.random.choice(self.data, num_vals)

    def get_normal_indexes(self, num_vals):
        sampled_values = np.array([])
        while True:
            normal_val = self.random.normal(NORMAL_MEAN, NORMAL_STD, num_vals)
            scaled_vals = normal_val * self.data_points
            scaled_vals = scaled_vals[scaled_vals >= 0]
            scaled_vals = scaled_vals[scaled_vals < self.data_points]
            sampled_values = np.append(sampled_values, scaled_vals)
            if len(sampled_values) > num_vals:
                additional_values_count = len(sampled_values) - num_vals
                sampled_values = sampled_values[:-additional_values_count]
                break
        idxs = np.clip(sampled_values, 0, self.data_points).astype(int)
        # import matplotlib.pyplot as plt
        # _, bins, _ = plt.hist(idxs, color='b')
        # plt.hist(np.sort(sampled_values), color='r', alpha=0.5)
        # plt.show()
        # import pdb; pdb.set_trace()
        return idxs

    def get_normal_val(self, num_vals=1):
        idxs = self.get_normal_indexes(num_vals)
        return self.data[idxs]


class StockProjector:
    def __init__(self, sampler):
        self.sampler = sampler

    def project(self, num_days, start_price):
        projected_prices = [start_price]
        sampled_day_changes = self.sampler.get_normal_val(num_days)
        for change in sampled_day_changes:
            projected_prices.append((1 + change) * projected_prices[-1])
        return projected_prices
