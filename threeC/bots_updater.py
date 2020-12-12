import configparser
import json

import pdb
import py3cw  # type: ignore
import yaml

import constants

KEYS_TO_UPDATE = ["strategy_list", "pairs"]


def update_config(d):
    for k in KEYS_TO_UPDATE:
        if k in d.keys():
            d[k] = json.dumps(d[k], separators=(",", ":"))
    return d


# def update_strategy(d):
#     d['strategy_list'] = json.dumps(d['strategy_list'], separators=(',', ':'))
#     return d
#
#
# def update_pairs(d):
#     d['pairs'] = json.dumps(d['pairs'], separators=(',', ':'))
#     return d


class AllBotsDef:
    def __init__(self, all_bot_config):
        self.all_bot_config = all_bot_config

    @property
    def available_bots(self):
        return list(self.all_bot_config.keys())

    def get_bot(self, bot_name):
        if bot_name not in self.available_bots:
            raise Exception("Bot does not exist")
        return BotDef(self.all_bot_config[bot_name])


class BotDef:
    def __init__(self, bot_config):
        self.bot_config = bot_config

    def as_payload(self):
        return update_config(self.bot_config)


config = configparser.ConfigParser()
config.read(f"{constants.CONFIG_ROOT}/config.ini")

with open(f"{constants.CONFIG_ROOT}/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

with open(f"{constants.CONFIG_ROOT}/bots.yaml") as bots_f:
    bots_def = yaml.load(bots_f, Loader=yaml.Loader)

# py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])
# account_info = account_info.AccountInfo(py3cw, real=False)
# bots_def['base_keiko']['strategy_list'][0] = json.dumps(bots_def['base_keiko']['strategy_list'][0])
# bots_def['base_keiko']['strategy_list'] = json.dumps(bots_def['base_keiko']['strategy_list'])
all_bots_def = AllBotsDef(bots_def)
test_bot_def = BotDef(bots_def["test"])
pdb.set_trace()
success, out = py3cw.request(
    entity="bots", action="create_bot", payload=test_bot_def.as_payload()
)
test_def["bot_id"] = out["id"]
test_def["allowed_deals_on_same_pair"] = 10
pdb.set_trace()

# TODO: Load the settings for the current bots. Set up a script to update all the bots to a slightly different base order size.
success, out = py3cw.request(
    entity="bots", action="update", action_id=str(test_def["id"]), payload=test_def
)

success, out = py3cw.request(
    entity="bots", action="create_bot", payload=bots_def["base_keiko"]
)
pdb.set_trace()
