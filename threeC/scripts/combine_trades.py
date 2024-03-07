from py3cw import request as cw_req
import configparser
import yaml
import deal_handlers
import argparse

import slack_updater

parser = argparse.ArgumentParser()
parser.add_argument("--bot_deals", action="store_true")
parser.add_argument("deals", type=int, nargs="+")

args = parser.parse_args()

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])
deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
if args.bot_deals:
    all_deals = deal_handler.get_bot_deals(scope="active")
else:
    all_deals = deal_handler.get_smart_deals(status="active")

total_base = 0
total_alt = 0
total_profit = 0
current_price = 0
for deal in all_deals:
    if deal.get_id() in args.deals:
        print(
            f"{deal.get_id()}  {deal.get_bought_volume():.2f}  {deal.get_alt_bought_volume():.2f}  {deal.get_average_price():.2f} {deal.get_current_profit():.2f}"
        )
        total_base += deal.get_bought_volume()
        total_alt += deal.get_alt_bought_volume()
        total_profit += deal.get_current_profit()
        current_price = deal.get_current_price()
print(f"Total     {total_base:.2f} {total_alt:.2f} {total_profit:.2f}")
break_even = current_price + (total_base + total_profit) / total_alt
print(f"New Deal  buy: {total_base / total_alt:.2f}  break-even: {break_even:.2f}")

total_base = 0
total_alt = 0
total_profit = 0
current_price = 0
for deal in all_deals:
    if deal.get_id() in args.deals:
        if input(f"Close deal {deal.get_id()}: ").lower() == "y":
            deal.close(py3cw)
            total_base += deal.get_bought_volume()
            total_alt += deal.get_alt_bought_volume()
            total_profit += deal.get_current_profit()
            current_price = deal.get_current_price()
print(f"Total     {total_base:.2f} {total_alt:.2f} {total_profit:.2f}")
break_even = current_price + (total_base + total_profit) / total_alt
print(f"New Deal  amount: {total_alt:.2f}  break-even: {break_even:.2f}")
