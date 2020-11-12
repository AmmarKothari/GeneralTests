import csv
import math

from py3cw import request as cw_req
import configparser
import yaml

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])


all_deals = []
with open('new_deals.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        all_deals.append(row)

with open('new_deals_info.csv', 'r', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        for i, old_deal in enumerate(all_deals):
            if old_deal['id'] == row['id']:
                all_deals[i] = row
                try:
                    old_deal['deal_id']
                except KeyError:
                    old_deal['deal_id'] = 1
                break
import pdb; pdb.set_trace()
start_index = 13

for deal in all_deals:
    if start_index > int(deal['id']):
        continue
    success, response = py3cw.request(entity='accounts', action='currency_rates',
                                      payload={'pair': deal['pair'], 'market_code': 'binance'})
    units_to_buy = math.floor(float(deal['amount']) / float(response['lotStep'])) * float(response['lotStep'])
    sale_price = math.floor(float(deal['sale_price']) / float(response['priceStep'])) * float(response['priceStep'])


    # import pdb; pdb.set_trace()
    # Version 2
    payload = {
        "account_id": 29165531,
        "pair": deal['pair'],
        "position": {
            "type": "sell",
            "units": {
                "value": units_to_buy
            },
            "order_type": "conditional",
            "conditional": {
                "price": {
                    "value": sale_price
                },
                "order_type": "market"

            },
        },
        "take_profit": {
            "enabled": "true"
        },
        "stop_loss": {
            "enabled": "false"
        }
    }
    print(payload)
    success, response = py3cw.request(entity='smart_trades_v2', action='new', payload=payload)

    # Version 1
    # payload = {
    #     'account_id': 29165531,
    #     'pair': deal['pair'],
    #     'units_to_buy': float(deal['amount']),
    #     'buy_price': float(deal['sale_price']),
    #     'buy_method': 'limit'
    # }
    #
    # print(payload)
    # success, response = py3cw.request(entity='accounts', action='currency_rates',
    #                                   payload={'pair': deal['pair'], 'market_code': 'binance'})
    # payload['buy_price'] = math.floor(payload['buy_price'] / float(response['priceStep'])) * float(response['priceStep'])
    # payload['units_to_buy'] = math.floor(payload['units_to_buy'] / float(response['lotStep'])) * float(response['lotStep'])
    # print(f"Sending trade with ID: {deal['id']}")
    # success, response = py3cw.request(entity='smart_trades', action='create_smart_sell', payload=payload)


    try:
        print(f'Placed trade with id number: {response["id"]}')
        deal["deal_id"] = response["id"]
    except ValueError:
        print('Deal failed i think')


