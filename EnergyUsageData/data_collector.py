import pdb

import requests

import constants

BASE_URL = 'https://developer.nrel.gov/api/cleap/v1/'
BASE_PARAMS = {'accept': 'application/json'}
class DataCollector:
    def __init__(self):
        self.api_key = constants.NREL_KEY

    def get_data(self, url, params):
        response = requests.get(url=url, params=params)
        return response.json()

    def get_info_for_specified_city_state(self, city, state):
        url = BASE_URL + 'cities'
        return self.get_city_state_data_for_url(url, city, state)

    def get_energy_expenditures_and_ghg_by_sector(self, city, state):
        url = BASE_URL + 'energy_expenditures_and_ghg_by_sector'
        return self.get_city_state_data_for_url(url, city, state)

    def get_city_state_data_for_url(self, url, city, state):
        state = state.upper()
        params = {'city': city, 'state_abbr': state, 'api_key': constants.NREL_KEY}
        params.update(BASE_PARAMS)
        data = self.get_data(url, params)
        return data
