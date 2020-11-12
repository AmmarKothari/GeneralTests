import datetime
from py3cw import request as cw_req
import configparser
import yaml
import csv

from deal_handlers import DealHandler

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])
py3cw.request(entity='users', action='change_mode', payload={'mode': 'real'})

deal_handler = DealHandler(py3cw, use_cache=True)
all_deals = deal_handler.get_all_deals()
# TODO: Try to find deals that were closed on 10/29 as an indicator of which deals need to be moved?
cutoff_time = datetime.datetime(year=2020, month=10, day=29)
open_deals = []
BAN_MESSAGE = 'Exchange account is banned. Check your account settings.'
for deal in all_deals:
    if deal['error_message'] == BAN_MESSAGE:
        open_deals.append(deal)

with open('open_trades.csv', 'w', newline='') as csvfile:
    fieldnames = open_deals[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for deal in open_deals:
        writer.writerow(deal)

import pdb; pdb.set_trace()

