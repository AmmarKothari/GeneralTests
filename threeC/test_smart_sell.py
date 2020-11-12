import csv
import math

from py3cw import request as cw_req
import configparser
import yaml

# Only going to try and trade a single pair for testing purposes
import account_info
# Issue
# 'ETH_IOTX', 'BTC_STEEM', 'BTC_HIVE', 'BTC_CVC', 'BTC_CVC'
PAIRS_OF_INTEREST = []
PAIRS_OF_INTEREST.reverse()

EXISTING_DEALS = [5656532, 5656533, 5656534, 1486028, 1486035, 1486140, 1486147, 1486155, 1486156, 1486211, 1486248, 1486252, 1486254, 1486257, 1486258, 1486259, 1486261, 1486262, 1486263, 1486265, 1486266, 1486268, 1486271, 1486272, 1486273, 1486278, 1486280, 1486281, 1486282, 1486283, 1486284, 1486287, 1486288, 1486290, 1486291, 1486294, 1486296, 1486297, 1486299, 1486301, 1486303, 1486304, 1486306, 1486309, 1486310, 1486312, 1486314, 1486315, 1486316, 1486317, 1486320, 1486321, 1486323, 1486324, 1486325, 1486326, 1486327, 1486328, 1486330, 1486332, 1486333, 1486335, 1486337, 1486339, 1486340, 1486341, 1486342, 1486343, 1486345, 1486346, 1486348, 1486349, 1486350, 1486352, 1486354, 1486356]
EXISTING_DEALS.reverse()

PERCENT_INCREASE = 2.0

for pair in PAIRS_OF_INTEREST:
    new_deals = []
    with open('new_deals.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['pair'] == pair:
                new_deals.append(row)

    config = configparser.ConfigParser()
    config.read("config_files/config.ini")

    with open("config_files/settings.yaml") as settings_f:
        settings = yaml.load(settings_f, Loader=yaml.Loader)

    py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])

    for deal_id in EXISTING_DEALS:
        success, response = py3cw.request(entity='smart_trades_v2', action='get_by_id', action_id=str(deal_id))
        if success:
            print(f"Could not find deal {deal_id}")
            EXISTING_DEALS.remove(deal_id)
        else:
            if response['pair'] != pair:
                continue
            if response['status']['type'] == 'cancelled':
                EXISTING_DEALS.remove(deal_id)
                continue
            print(f'Cancelling deal: {deal_id} for pair {response["pair"]}')
            success, response = py3cw.request(entity='smart_trades_v2', action='cancel', action_id=str(deal_id))

    deal = new_deals[0]
    success, pair_market_data = py3cw.request(entity='accounts', action='currency_rates', payload={'pair': deal['pair'], 'market_code': 'binance'})

    account = account_info.AccountInfo(py3cw)
    exchange_account_id = account.accounts[1]['id']
    amount_in_account = account.get_coin_in_account(pair.split('_')[1], exchange_account_id)
    if not amount_in_account:
        print('ERROR: No coin in account for {}'.format(pair))
        continue
    deal_amount = min(float(deal['amount']), amount_in_account)
    if not deal_amount:
        import pdb; pdb.set_trace()
    if deal_amount < float(deal['amount']):
        print(f'There was less coin than the original deal requested. {deal_amount} < {deal["amount"]}')

    units_to_buy = math.floor(deal_amount / float(pair_market_data['lotStep'])) * float(pair_market_data['lotStep'])
    sale_price = math.floor(float(deal['sale_price']) / float(pair_market_data['priceStep'])) * float(pair_market_data['priceStep'])

    # Version 2
    payload = {
        "account_id": 29165531,
        "pair": deal['pair'],
        "skip_enter_step": True,
        "position": {
            "type": "buy",
            "order_type": "market",
            "units": {
                "value": units_to_buy
            },
            "price": {
                    "value": sale_price
            },
        },

        "take_profit": {
            "enabled": "true",
            "steps": [
                {
                    "order_type": "limit",
                    "price": {
                        "type": "bid",
                        "value": sale_price * (1.0 + PERCENT_INCREASE / 100),
                        # "percent": 2.0,
                    },
                    "volume": 100
                }
            ]
        },

        "stop_loss": {
            "enabled": "false"
        }
    }

    success, response = py3cw.request(entity='smart_trades_v2', action='new', payload=payload)
    if success:
        print(payload)
        print(f'There was an error: {success}')
    print(f'Created trade for {response["pair"]}')
