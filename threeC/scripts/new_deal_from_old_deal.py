import csv
import math
import sys
import datetime
import argparse

from py3cw import request as cw_req
import configparser
import yaml
import deal_handlers

import account_info
import slack_updater

DEAL_OF_INTEREST = 1519166

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

# Get all safety orders
deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
all_smart_deals = deal_handler.get_smart_deals(status="active")
# Sort by oldest to newest
all_smart_deals.sort(key=lambda x: x.get_created_at())

for smart_deal in all_smart_deals:
    if smart_deal.get_id() == DEAL_OF_INTEREST:
        trades = smart_deal.get_trades(py3cw)
        buys = []
        sells = []
        for trade in trades:
            if trade.is_buy():
                buys.append(trade)
            else:
                sells.append(trade)
        base_total = 0
        alt_total = 0
        for buy in buys:
            if buy.is_completed():
                base_total += buy.base_amount()
                alt_total += buy.alt_amount()
        for sell in sells:
            if sell.is_completed():
                base_total -= sell.base_amount()
                alt_total -= sell.alt_amount()
