import pdb

import pytest
import requests

import constants
import data_collector

SAN_FRANCISCO = 'San Francisco'
CA = 'CA'


@pytest.fixture
def dc():
    return data_collector.DataCollector()


@pytest.fixture
def test_url():
    return 'https://developer.nrel.gov/api/alt-fuel-stations/v1.json?fuel_type=E85,ELEC&state=CA&limit=2&api_key={}'.format(
        constants.NREL_KEY)


def test_get_data(test_url, dc):
    params = {}
    data = dc.get_data(test_url, params)
    assert data is not None


def test_get_info_for_specified_city_state(dc):
    data = dc.get_info_for_specified_city_state(SAN_FRANCISCO, CA)
    assert data is not None


def test_get_energy_expenditures_and_ghg_by_sector(dc):
    data = dc.get_energy_expenditures_and_ghg_by_sector(SAN_FRANCISCO, CA)
    pdb.set_trace()
    assert data is not None
