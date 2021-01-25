import datetime
import time
import sys
import configparser
import os
import yaml
from tendo import singleton
import collections


from py3cw import request as py3cw_req

import account_info as account_info_module
import constants
import deal_handlers
import gsheet_writer
import threeCDataGetter as tcdg
from bot_info import BotInfo
from constants import LAST_RUN_SUCCESS_CACHE
from deal_handlers import DealHandler
import slack_updater

lock = singleton.SingleInstance()

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = py3cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

account_info = account_info_module.AccountInfo(py3cw, real=True)
account_id = account_info.account_ids[settings["MAIN_ACCOUNT_KEY"]]
table = account_info.account_table_data(account_id)

not_in_order_raw = collections.OrderedDict()
for t in table:
    amount_free = t['equity'] - t['on_orders']
    not_in_order_raw[t['currency_code']] = {'free': amount_free,
                                        'value_usd': amount_free * t['current_price_usd']
                                            }
not_in_order = sorted(not_in_order_raw.items(), key=lambda x: x[1]['value_usd'], reverse=True)


for coin in not_in_order:
    if coin[1]['value_usd'] > 10.0:
        btc_pair = "BTC_{}".format(coin[0])
        success, response = py3cw.request(entity="accounts", action="currency_rates", payload={"pair": btc_pair, "market_code": "binance"})
        if response:
            max_book_price = float(response['maxPrice'])
        else:
            max_book_price = -1
        print(f"{coin[0]:<5}  {coin[1]['free']:10.3f}  {coin[1]['value_usd']:8.3f} USD  Max Book Price: {max_book_price:8.3f}")
import pdb; pdb.set_trace()

