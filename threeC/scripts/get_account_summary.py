import configparser
from py3cw import request as cw_req
import yaml
import csv

import account_info
from utils import config_utils

py3cw = config_utils.get_3c_interface()
settings = config_utils.get_settings()

account = account_info.AccountInfo(py3cw)
primary_account = settings["EXCHANGE_ACCOUNT_NAMES"][0]
exchange_account = account.get_account_from_name(primary_account)
coin_data = account.account_table_data(exchange_account['id'])

with open("current_coin_amounts.csv", "w", newline="") as csvfile:
    fieldnames = coin_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in coin_data:
        writer.writerow(data)
