import configparser
from py3cw import request as cw_req
import yaml
import csv

import account_info

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)
#
# # From the old 3c binance account
py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])
# account = account_info.AccountInfo(py3cw)
# exchange_account_id = account.accounts[1]['id']
# coin_data = account.account_table_data(exchange_account_id)

all_coin_data = []
with open("current_coin_amounts_orig.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        all_coin_data.append(row)

# Into my 3c binance account
from binance import client as bclient

client = bclient.Client(api_key, api_secret)


# threec_client = bclient.Client(, config['threeC']['secret'])

# Binance Market type
for coin_data in all_coin_data:
    destination_info = client.get_deposit_address(asset=coin_data["currency_code"])
    import pdb

    pdb.set_trace()
    if not destination_info["success"]:
        print(
            f"Could not find destination address for coin {coin_data['currency_code']}"
        )
        continue
    coin_data["destination_info"] = destination_info
    print(
        f"{coin_data['currency_code']} address in binance account: {coin_data['destination_info']['address']}"
    )

with open("currency_destination_info.csv", "w", newline="") as csvfile:
    fieldnames = all_coin_data[0]["destination_info"].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for coin_data in all_coin_data:
        if "destination_info" in coin_data.keys():
            writer.writerow(coin_data["destination_info"])

# PERL
