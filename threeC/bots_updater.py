import configparser
import json

import pdb
from py3cw import request as cw_req

import yaml

config = configparser.ConfigParser()
config.read("config.ini")

with open("settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

with open("bots.yaml") as bots_f:
    bots_def = yaml.load(bots_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])
# pdb.set_trace()
# bots_def['base_keiko']['strategy_list'][0] = json.dumps(bots_def['base_keiko']['strategy_list'][0])
# bots_def['base_keiko']['strategy_list'] = json.dumps(bots_def['base_keiko']['strategy_list'])
success, out = py3cw.request(entity='bots', action='create_bot', payload=bots_def['base_keiko'])
pdb.set_trace()