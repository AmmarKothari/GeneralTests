from py3cw import request as cw_req
import configparser
import yaml
import deal_handlers
import traceback

import slack_updater

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

# Get all safety orders
deal_handler = deal_handlers.DealHandler(py3cw, use_cache=True)
all_bot_deals = deal_handler.get_bot_deals(scope="active")
all_bot_deals.sort(key=lambda x: x.get_created_at())

new_convert_trades_message = []
converted_deals_counter = 0
for deal in all_bot_deals:
    if converted_deals_counter >= settings['CONVERT_SMART_TRADE']['MAX_CONVERT']:
        break
    print(f'Active safety orders: {deal.get_active_safety_orders()}')
    if deal.open_duration().total_seconds() > settings['CONVERT_SMART_TRADE']['THRESHOLD']:
        try:
            deal.convert_to_smart_deal(py3cw)
        except Exception as e:
            print(f'Exception: {traceback.format_exc()}')
            continue
        new_convert_trades_message.append(f"Converted order {deal.get_id()} to smart trade. "
                                          f"Open for {deal.open_duration().total_seconds()/60/60/24:.2f} days.")
        converted_deals_counter += 1
        print(f'Converting deal {deal}')
    else:
        print(f'Not converting deal {deal}')

if new_convert_trades_message:
    su = slack_updater.SlackUpdater(config["threeC"]["slack_bot_token"])
    su.send_status_message("\n".join(new_convert_trades_message))
