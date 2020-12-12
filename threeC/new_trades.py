import csv

from binance import client as bclient
from binance import exceptions as bexceptions


from py3cw import request as cw_req
import configparser
import yaml

open_trades = []
with open("orig_open_trades.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        open_trades.append(row)

all_trade_pairs = set()
for trade in open_trades:
    all_trade_pairs.add(trade["pair"])
all_trade_pairs = list(all_trade_pairs)
all_trade_pairs = sorted(all_trade_pairs, key=str.lower)

IGNORE_KEYS = ["created_at", "updated_at", "closed_at"]
ACCUMULATE_KEYS = [
    "id",
    "base_order_volume",
    "bought_amount",
    "bought_volume",
    "bot_id",
    "bought_average_price",
    "safety_order_volume",
    "actual_profit",
    "actual_usd_profit",
    "bot_name",
    "reserved_base_coin",
    "reserved_second_coin",
    "completed_manual_safety_orders_count",
    "sold_amount",
    "current_active_safety_orders_count",
    "sold_volume",
    "completed_safety_orders_count",
    "sold_average_price",
]

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

id = 0
new_deals = []

trade_pairs = {}
for pair in all_trade_pairs:
    trade_pairs[pair] = {}
    for key in ACCUMULATE_KEYS:
        trade_pairs[pair][key] = []
    for trade in open_trades:
        if trade["pair"] == pair:
            for key in trade.keys():
                if key not in trade_pairs[pair].keys():
                    trade_pairs[pair][key] = trade[key]
                elif key in trade_pairs[pair].keys() and key in ACCUMULATE_KEYS:
                    trade_pairs[pair][key].append(trade[key])
                elif trade_pairs[pair][key] != trade[key] and key not in IGNORE_KEYS:
                    print("KEY: ", key)
                    import pdb

                    pdb.set_trace()
                else:
                    # Same value so just keep going
                    pass
    amount_bought = sum([float(amt) for amt in trade_pairs[pair]["bought_amount"]])
    weighted_price = (
        sum(
            [
                float(avg) * float(amt)
                for avg, amt in zip(
                    trade_pairs[pair]["bought_average_price"],
                    trade_pairs[pair]["bought_amount"],
                )
            ]
        )
        / amount_bought
    )
    sale_price = weighted_price * (1 + float(trade_pairs[pair]["take_profit"]) / 100.0)
    base = pair.split("_")[0]
    alt = pair.split("_")[1]

    # try:
    #     bpair = pair.split('_')[1] + pair.split('_')[0]
    #     current_price = float(client.get_avg_price(symbol=bpair)['price'])
    #     percent_increase = (sale_price - current_price) / current_price
    # except bexceptions.BinanceAPIException:
    #     percent_increase = 'N/A'
    success, all_market_pairs = py3cw.request(
        entity="accounts", action="market_pairs", payload={"market_code": "binance"}
    )

    try:
        success, response = py3cw.request(
            entity="accounts",
            action="currency_rates",
            payload={"pair": pair, "market_code": "binance"},
        )
        current_price = float(response["last"])
        percent_increase = (sale_price - current_price) / current_price
    except TypeError:
        print("Error with pair: {}".format(pair))
        # import pdb; pdb.set_trace()
        continue

    # TODO: Check min lot size
    # TODO: Check that it fits with the step size
    # TODO: Check that the sale price is greater than the current price
    # TODO: Check that there is at least that much in the account.

    id += 1
    print(
        f"ID: {id:<3} | Pair: {pair:<10} | Sell {amount_bought:<15.3f} {alt:<5} at {sale_price:<10.8f} {base} | {percent_increase*100:.2f} % increase"
    )

    new_deals.append(
        {
            "pair": pair,
            "id": id,
            "amount": amount_bought,
            "sale_price": sale_price,
            "percent_increase": percent_increase * 100,
        }
    )

with open("new_deals.csv", "w", newline="") as csvfile:
    fieldnames = new_deals[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data in new_deals:
        writer.writerow(data)
