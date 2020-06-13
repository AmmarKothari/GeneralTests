import functools

from threeCDataGetter import _check_if_request_successful


class BotInfo:
    def __init__(self, cw, account_id):
        self.account_id = account_id
        self.cw = cw

    @property
    @functools.lru_cache()
    def strategy_list(self):
        success, response = self.cw.request(entity='bots', action='strategy_list', payload={'account_id': self.account_id})
        _check_if_request_successful(success)
        return response.keys()

    def get_strategy(self, strategy_name):
        return self.strategy_list[strategy_name]
