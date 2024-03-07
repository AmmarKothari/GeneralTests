from tendo import singleton
import collections

from py3cw import request as py3cw_req

import account_info as account_info_module
from utils import config_utils

lock = singleton.SingleInstance()

settings = config_utils.get_settings()

py3cw = config_utils.get_3c_interface()

account_info = account_info_module.AccountInfo(py3cw, real=True)

for account_name in settings["EXCHANGE_ACCOUNT_NAMES"]:
    print("******{}******".format(account_name))
    account_id = account_info.account_ids[account_name]
    table = account_info.account_table_data(account_id)

    not_in_order_raw = collections.OrderedDict()
    for t in table:
        amount_free = t["equity"] - t["on_orders"]
        not_in_order_raw[t["currency_code"]] = {
            "free": amount_free,
            "value_usd": amount_free * t["current_price_usd"],
        }
    not_in_order = sorted(
        not_in_order_raw.items(), key=lambda x: x[1]["value_usd"], reverse=True
    )

    for coin in not_in_order:
        if coin[1]["value_usd"] > 10.0:
            btc_pair = "BTC_{}".format(coin[0])
            success, response = py3cw.request(
                entity="accounts",
                action="currency_rates",
                payload={"pair": btc_pair, "market_code": "binance"},
            )
            if response:
                max_book_price = float(response["maxPrice"])
            else:
                max_book_price = -1
            print(
                f"{coin[0]:<5}  {coin[1]['free']:10.3f}  {coin[1]['value_usd']:8.3f} USD  Max Book Price: {max_book_price:8.3f}"
            )
