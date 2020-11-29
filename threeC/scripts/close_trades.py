import configparser
from py3cw import request as cw_req
import yaml
import csv

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

open_trades = []
with open("open_trades.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        open_trades.append(row)

all_trade_pairs = set()
for trade in open_trades:
    all_trade_pairs.add(trade["pair"])

trade_pairs = {}
total_trades = 0
for pair in all_trade_pairs:
    trade_pairs[pair] = []
    for trade in open_trades:
        if trade["pair"] == pair:
            total_trades += 1
            trade_pairs[pair].append(trade["id"])

# for trade_pair, trade_ids in trade_pairs.items():
#     for trade_id in trade_ids:
#         import pdb; pdb.set_trace()
#         success, response = py3cw.request(entity='deals', action='cancel', action_id=trade_id)
