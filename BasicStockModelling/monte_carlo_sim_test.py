import datetime

import monte_carlo_sim
import pytest
import numpy as np

# ---------------------------------
# Load Historical Data
# ---------------------------------
@pytest.fixture('session')
def historical_price_data():
    historical_data = monte_carlo_sim.LoadHistoricalData('PG')
    historical_data.load_data_for_date_range(start=datetime.date(2019, 1, 1), end=datetime.date(2020, 1, 10))
    return historical_data.get_price_change_data()


def test_get_data_for_date_range(historical_price_data):
    assert historical_price_data is not None


def test_get_data_for_start_and_duration():
    historical_data = monte_carlo_sim.LoadHistoricalData('PG')
    historical_data.load_data_for_date_range(start=datetime.date(2020, 1, 1), duration=10)
    return historical_data.get_price_change_data()


def test_get_data_for_end_and_duration():
    historical_data = monte_carlo_sim.LoadHistoricalData('PG')
    historical_data.load_data_for_date_range(end=datetime.date(2020, 1, 10), duration=10)
    return historical_data.get_price_change_data()


# ---------------------------------
# Stock Change Sampler
# ---------------------------------
@pytest.fixture
def stock_change_sampler(historical_price_data):
    return monte_carlo_sim.StockChangeSampler(historical_price_data)


def test_get_uniform_val_single(stock_change_sampler):
    assert stock_change_sampler.get_uniform_val()
    assert len(stock_change_sampler.get_uniform_val()) == 1


def test_get_uniform_val_multiple(stock_change_sampler):
    assert len(stock_change_sampler.get_uniform_val(2)) == 2


def test_get_normal_indexes(stock_change_sampler):
    normal_idxs = stock_change_sampler.get_normal_indexes(600)
    assert len(normal_idxs) == 600
    assert abs(np.mean(normal_idxs) - stock_change_sampler.data_points/2.0) < 5.0


def test_get_normal_val(stock_change_sampler):
    assert stock_change_sampler.get_normal_val()
    assert len(stock_change_sampler.get_normal_val()) == 1


def test_get_normal_val_multiple(stock_change_sampler):
    assert len(stock_change_sampler.get_normal_val(2)) == 2


# ---------------------------------
# Stock Projector
# ---------------------------------
@pytest.fixture
def stock_projector(stock_change_sampler):
    return monte_carlo_sim.StockProjector(stock_change_sampler)


def test_project(stock_projector):
    projection = stock_projector.project(10, 100)
    assert len(projection) == 11
