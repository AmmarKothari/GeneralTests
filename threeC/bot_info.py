import functools
from typing import Optional, List, Any, Dict
import yaml

import py3cw  # type: ignore

import request_helper


BOTS_FILENAME = "bots.yaml"
# TODO: Verify all of these types


class BotInfo:
    def __init__(self, cw: py3cw.request.Py3CW, account_id: Optional[int] = None):
        self.account_id = account_id
        self.cw = cw

    @property
    @functools.lru_cache()
    def strategy_list(self) -> Dict[str, Any]:
        if not self.account_id:
            raise Exception("Account ID not set.")
        success, response = self.cw.request(
            entity="bots",
            action="strategy_list",
            payload={"account_id": self.account_id},
        )
        request_helper.check_if_request_successful(success)
        return response.keys()

    def get_strategy(self, strategy_name) -> Dict[str, Any]:
        return self.strategy_list[strategy_name]

    @property
    @functools.lru_cache()
    def bots(self) -> request_helper.Py3cw_request_info_list:
        success, bots = self.cw.request(entity="bots", action="")
        request_helper.check_if_request_successful(success)
        return bots


def _load_yaml():
    with open(BOTS_FILENAME) as bot_yaml:
        settings_dict = yaml.load(bot_yaml)
    return settings_dict


class GridBots:
    def __init__(self, cw: py3cw.request.Py3CW):
        self.cw = cw

    @property
    @functools.lru_cache()
    def bots(self):
        success, bots = self.cw.request(entity="grid_bots", action="")
        request_helper.check_if_request_successful(success)
        return bots

    @property
    def ids(self):
        ids = []
        for bot in self.bots:
            ids.append(bot['id'])
        return ids

    def get_pair(self, bot_id: int):
        for bot in self.bots:
            if bot['id'] == bot_id:
                return bot['pair']

    def get_profits(self, bot_id: int = 0):
        profits = []
        for bot in self.bots:
            if bot_id:
                if bot['id'] != bot_id:
                    continue
            id = bot['id']
            success, one_bot_profits = self.cw.request(entity="grid_bots", action="profits", action_id=str(id))
            request_helper.check_if_request_successful(success)
            profits.extend(one_bot_profits)
        return profits



