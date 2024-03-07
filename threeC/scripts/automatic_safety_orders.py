import math
import datetime

import yaml
import deal_handlers

import account_info
from utils import config_utils


settings = config_utils.get_settings()
py3cw = config_utils.get_3c_interface()

UPDATE_TIME_THRESHOLD = 60 * 60 * 24  # 1 Day

# Get total coin
accounts = account_info.AccountInfo(py3cw)

# Get all safety orders
deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
all_smart_deals = deal_handler.get_smart_deals(status="active")
all_smart_deals.sort(key=lambda x: x.get_created_at())
CURRENCY_SETTINGS = {
    "BTC": {
        "min": 0.05,
        "base_order_size": 0.002,
        "ratio_of_order_price": 0.95,
    },
    "ETH": {
        "min": 0.5,
        "base_order_size": 0.02,
        "ratio_of_order_price": 0.95,
    },
    "BNB": {
        "min": 5.0,
        "base_order_size": 0.2,
        "ratio_of_order_price": 0.95,
    },
    "USDT": {
        "min": 200.0,
        "base_order_size": 20,
        "ratio_of_order_price": 0.95,
    },
    "USD": {
        "min": 200.0,
        "base_order_size": 20,
        "ratio_of_order_price": 0.95,
    }
}

# Don't open more than this number of deals to help limit total spend.
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
        for smart_deal in all_smart_deals:
            if smart_deal.get_base_currency() != base_currency:
                print(f"Base currency of deal does not match {smart_deal.get_base_currency()} != {base_currency}")
                continue
            if not smart_deal.is_open():
                print(f"Deal {smart_deal.get_id()} ({smart_deal.get_pair()}) has not been opened so can't add funds.")
                continue

            try:
                smart_trade_trades = smart_deal.get_trades(py3cw)
            except deal_handlers.GetTradesException as e:
                print(f"{smart_deal.get_pair()} Exception when getting trade info {e}")
                continue

            most_recent_update = max([t.get_updated_at() for t in smart_trade_trades])
            time_delta = datetime.datetime.utcnow() - most_recent_update
            if time_delta.total_seconds() < UPDATE_TIME_THRESHOLD:
                print(f'{smart_deal.get_pair():<10} deal has been updated recently. ({time_delta.seconds}s < {UPDATE_TIME_THRESHOLD}s) Not adding safety order.')
                continue

            # When is the right time to count a deal?
            deal_count += 1
            print(f'Deal count {deal_count}')
            if deal_count > MAX_NUMBER_OF_DEALS:
                print(f'Exceeded the max number of deals for currency ({MAX_NUMBER_OF_DEALS})')
                break

            # Get acceptable order size
            # This is not going to work for the other account unfortuantely.
            success, response = py3cw.request(entity="accounts", action="currency_rates", payload={"pair": smart_deal.get_pair(), "market_code": account["market_code"]})
            if success:
                print(f'Error getting trade info: {success}')
                continue
            amount = CURRENCY_SETTINGS[base_currency]["base_order_size"] / float(response['last'])
            units_to_buy = math.floor(
                float(amount) / float(response["lotStep"])
            ) * float(response["lotStep"])

            buy_price = float(response['last']) * CURRENCY_SETTINGS[base_currency]["ratio_of_order_price"]
            try:
                smart_deal.add_safety_order(py3cw, "limit", units_to_buy, buy_price)
            except deal_handlers.AddFundsException as e:
                deal_count -= 1
                continue
            print(f"{smart_deal.get_id()}: Created a new safety order for {smart_deal.get_pair()}")
            new_safety_order_msgs.append(f"{smart_deal.get_id()}: Created a new safety order for {smart_deal.get_pair()}")

print("New Safety order summary:")
print("\n".join(new_safety_order_msgs))
if not new_safety_order_msgs:
    new_safety_order_msgs = ["No update today"]
if new_safety_order_msgs:
    su = config_utils.get_slack_updater()
    su.send_status_message("\n".join(new_safety_order_msgs))



