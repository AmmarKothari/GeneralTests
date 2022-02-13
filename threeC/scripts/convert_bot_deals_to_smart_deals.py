from py3cw import request as cw_req
import configparser
import yaml
import deal_handlers

import slack_updater

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

# Get all safety orders
deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
all_bot_deals = deal_handler.get_bot_deals(scope="active")

new_convert_trades_message = []
for deal in all_bot_deals:
    print(f'Active safety orders: {deal.get_active_safety_orders()}')
    if deal.open_duration().total_seconds() > settings["CONVERT_SMART_TRADE_DURATION"]:
        deal.convert_to_smart_deal(py3cw)
        new_convert_trades_message.append(f"Converted order {deal.get_id()} to smart trade.")
        print(f'Converting deal {deal}')
    else:
        print(f'Not converting deal {deal}')

if new_convert_trades_message:
    su = slack_updater.SlackUpdater(config["threeC"]["slack_bot_token"])
    su.send_status_message("\n".join(new_convert_trades_message))
