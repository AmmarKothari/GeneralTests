import configparser
from py3cw import request as cw_req
import yaml
import csv

import account_info
from utils import config

py3cw = config.get_3c_interface()

account = account_info.AccountInfo(py3cw)
exchange_account_id = account.accounts[1]["id"]
coin_data = account.account_table_data(exchange_account_id)

with open("current_coin_amounts.csv", "w", newline="") as csvfile:
    fieldnames = coin_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in coin_data:
        writer.writerow(data)
