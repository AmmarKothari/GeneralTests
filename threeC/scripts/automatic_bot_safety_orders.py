import math
import datetime

from py3cw import request as cw_req
import configparser
import yaml
import deal_handlers

import account_info
import slack_updater

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

MIN_IN_ACCOUNT = 0.01  # MINIMUM AMOUNT OF COIN IN ACCOUNT TO DO THIS
UPDATE_TIME_THRESHOLD = 60 * 60 * 24  # 1 Day

# Get total coin
accounts = account_info.AccountInfo(py3cw)

# Get all safety orders
deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
all_bot_deals = deal_handler.get_bot_deals(scope="active")
# Sort by oldest to newest
all_bot_deals.sort(key=lambda x: x.get_created_at())

# Uses safety order size to place orders
CURRENCY_SETTINGS = {
    "BTC": {
        "min": 0.2,
        "ratio_of_order_price": 0.95,
    },
    "ETH": {
        "min": 1.0,
        "ratio_of_order_price": 0.95,
    },
    "BNB": {
        "min": 5.0,
        "ratio_of_order_price": 0.95,
    },
    "USDT": {
        "min": 200.0,
        "ratio_of_order_price": 0.95,
    },
    "USD": {
        "min": 200.0,
        "ratio_of_order_price": 0.95,
    },
}

# Don't open more than this number of deals to help limit total spend.
ACTIVE_SAFETY_ORDER_MIN = 100
MAX_NUMBER_OF_DEALS = 20

new_safety_order_msgs = []
for account in [accounts.get_account_from_name(account_name) for account_name in settings["EXCHANGE_ACCOUNT_NAMES"]]:
    print(f"****Analyzing account {account['name']}****")
    for base_currency in CURRENCY_SETTINGS:
        print(f'Base Currency: {base_currency}')
        min_in_account = CURRENCY_SETTINGS[base_currency]["min"]
        # Check there is a enough coin in account
        try:
            coin_in_account = accounts.get_coin_available(base_currency, account["id"])
        except account_info.AccountException as e:
            print(e)
            continue
        if coin_in_account < min_in_account:
            print(f"{coin_in_account:.6f} < {min_in_account:.6f} so not going to open more safety orders")
            continue

        deal_count = 0
        for bot_deal in all_bot_deals:
            if bot_deal.get_base_currency() != base_currency:
                print(f"{bot_deal.get_id()}: Base currency of deal does not match {bot_deal.get_base_currency()} != {base_currency}")
                continue

            if bot_deal.get_active_safety_orders() > ACTIVE_SAFETY_ORDER_MIN:
                print(f"{bot_deal.get_id()}: Active safety orders more than minimum {bot_deal.get_active_safety_orders()} <= {ACTIVE_SAFETY_ORDER_MIN}")
                continue

            time_delta = datetime.datetime.utcnow() - bot_deal.get_updated_at()
            if time_delta.total_seconds() < UPDATE_TIME_THRESHOLD:
                print(f'{bot_deal.get_id()}: {bot_deal.get_pair()} deal has been updated recently. ({time_delta.seconds}s < {UPDATE_TIME_THRESHOLD}s) Not adding safety order.')
                continue

            # When is the right time to count a deal?
            deal_count += 1
            print(f'Deal count {deal_count}')
            if deal_count > MAX_NUMBER_OF_DEALS:
                print(f'Exceeded the max number of deals for currency ({MAX_NUMBER_OF_DEALS})')
                break

            # Get acceptable order size
            try:
                response = bot_deal.get_data_for_adding_funds(py3cw)
            except:
                print('Unexplained Exception')
                continue
            amount = float(bot_deal.deal['base_order_volume']) / float(response['orderbook_price'])
            units_to_buy = math.floor(
                float(amount) / float(response["limits"]["lotStep"])
            ) * float(response["limits"]["lotStep"])

            buy_price_raw = float(response['orderbook_price']) * CURRENCY_SETTINGS[base_currency]["ratio_of_order_price"]
            # Taking the slightly lower price
            buy_price = math.floor(buy_price_raw / float(response['limits']['priceStep'])) * float(response['limits']['priceStep'])

            if units_to_buy <= float(response['limits']['minLotSize']):
                print("Too small of an order.  Skipping")
            if units_to_buy >= float(response['limits']['maxLotSize']):
                print("Too large of an order.  Skipping")
            if buy_price <= float(response['limits']['minPrice']):
                print("Buy price is too low.")
            if buy_price >= float(response['limits']['maxPrice']):
                print("Buy price is too high.")
            try:
                pass
                bot_deal.add_funds(py3cw, units_to_buy, buy_price, False)
            except deal_handlers.AddFundsException as e:
                print(e)
                deal_count -= 1
                continue
            new_safety_order_msgs.append(f"{bot_deal.get_id()}: Created a new safety order for {bot_deal.get_pair()}")
print("New Safety order summary:")
print("\n".join(new_safety_order_msgs))
if not new_safety_order_msgs:
    new_safety_order_msgs = ["No update today"]

su = slack_updater.SlackUpdater(config["threeC"]["slack_bot_token"])
su.send_status_message("\n".join(new_safety_order_msgs))
