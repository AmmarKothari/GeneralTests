import functools

import yaml

from request_helper import _check_if_request_successful

BOTS_FILENAME = 'bots.yaml'


class BotInfo:
    def __init__(self, cw, account_id=None):
        self.account_id = account_id
        self.cw = cw

    @property
    @functools.lru_cache()
    def strategy_list(self):
        if not self.account_id:
            raise Exception('Account ID not set.')
        success, response = self.cw.request(entity='bots', action='strategy_list', payload={'account_id': self.account_id})
        _check_if_request_successful(success)
        return response.keys()

    def get_strategy(self, strategy_name):
        return self.strategy_list[strategy_name]

    @property
    @functools.lru_cache()
    def bots(self):
        success, bots = self.cw.request(entity='bots', action='')
        _check_if_request_successful(success)
        return bots


def _load_yaml():
    with open(BOTS_FILENAME) as bot_yaml:
        settings_dict = yaml.load(bot_yaml)
    return settings_dict