import configparser
from py3cw import request as cw_req
import yaml
import csv

import account_info

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)
py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

account = account_info.AccountInfo(py3cw)
exchange_account_id = account.accounts[1]["id"]
coin_data = account.account_table_data(exchange_account_id)

with open("current_coin_amounts.csv", "w", newline="") as csvfile:
    fieldnames = coin_data[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in coin_data:
        writer.writerow(data)
