from py3cw import request as cw_req
import configparser
import yaml
import deal_handlers
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--bot_deals", action="store_true")

args = parser.parse_args()

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
all_bot_deals = deal_handler.get_bot_deals(scope="active")
all_smart_deals = deal_handler.get_smart_deals(status="active")
for deal in all_bot_deals + all_smart_deals:
    print(
        f"{deal.get_id()}  {deal.get_pair():<8} {deal.get_bought_volume():.6f} {deal.get_alt_bought_volume():.2f} {deal.get_average_price():.2f} {deal.get_current_profit():.2f}"
    )
