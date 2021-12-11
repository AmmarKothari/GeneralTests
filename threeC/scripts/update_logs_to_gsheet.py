import datetime
import time
import sys
import configparser
import os
import yaml
from tendo import singleton


from py3cw import request as py3cw_req

import account_info as account_info_module
import constants
import deal_handlers
import gsheet_writer
import threeCDataGetter as tcdg
from bot_info import BotInfo
from constants import LAST_RUN_SUCCESS_CACHE
from deal_handlers import DealHandler
import slack_updater

# TODO: "max_simultaneous_deals",
FIELDS_OF_INTEREST = ["id", "bot_id", "created_at", "finished?", "current_active_safety_orders", "completed_safety_orders_count", "completed_manual_safety_orders_count", "pair", "status", "take_profit", "base_order_volume", "bought_volume", "sold_volume", "error_message", "from_currency", "to_currency", "final_profit_percentage", "actual_profit_percentage", "bot_name", "actual_profit", "bot_group"]

lock = singleton.SingleInstance()

config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = py3cw_req.Py3CW(key=config["threeC"]["key"], secret=config["threeC"]["secret"])

su = slack_updater.SlackUpdater(config["threeC"]["slack_bot_token"])

try:
    print(
        "Starting calculation at {}".format(
            datetime.datetime.now().strftime("%D - %H:%M")
        )
    )
    start_time = time.time()
    gwriter = gsheet_writer.GSheetWriter(
        os.path.expanduser(settings["GSHEET_SERVICE_FILE"]), settings["GSHEET_LOG_FILE"]
    )


    print("Starting writing account stats")
    account_info = account_info_module.AccountInfo(py3cw, real=True)
    account_stats = []
    for account_name in settings["EXCHANGE_ACCOUNT_NAMES"]:
        account_stats.append(account_info.get_account_stats(account_name))
    accumulated_account_stats = gwriter.combine_account_stats(account_stats)
    gwriter.write_account_stats(
        settings["GSHEET_TAB_NAME_ACCOUNT_VALUE"], accumulated_account_stats
    )
    print("Finished writing account stats")
    bot_info = BotInfo(py3cw)

    # TODO: Clear sheet before writing
    # gwriter.write_bot_id_to_names_map_to_gsheet(
    #     bot_info.bots, settings["GSHEET_TAB_NAME_BOT_IDS"]
    # )
    deal_handler = DealHandler(py3cw)
    print("Loading raw deals from cache")
    deal_handler.use_cache_deals()
    print("Fetching deals from 3c")
    all_new_deals = deal_handler.api_deal_handler.get_deals(deal_handler.raw_deal_cacher.most_recent_update_time())
    print("Updating files")
    deal_handler.update_deals(all_new_deals)
    print("Updating raw deals cache file")
    deal_handler.raw_deal_cacher.cache_deals_to_file(deal_handler.all_deals)
    data = deal_handler.all_deals
    data = deal_handlers.get_data(py3cw, deal_handler, use_cache=True)
    print("Finished getting data from ThreeC")

    filtered_deals = []
    for bot_group_key in settings["bot_groups"]:
        for bot_id in settings["bot_groups"][bot_group_key]:
            bot_deals = tcdg.filter_by_bot_id(data, bot_id)
            for deal in bot_deals:
                deal["bot_group"] = bot_group_key
            filtered_deals.extend(bot_deals)
    print("Finished filtering deals based on bot groups")
    unique_deals = []
    unique_deal_ids = []
    for deal in filtered_deals:
        if deal["id"] not in unique_deal_ids:
            unique_deal_ids.append(deal["id"])
            unique_deals.append(deal)
    unique_deals = sorted(unique_deals, key=lambda x: int(x["id"]), reverse=True)
    unique_deals_with_relevant_fields = []
    for deal in unique_deals:
        unique_deals_with_relevant_fields.append({k: deal[k] for k in FIELDS_OF_INTEREST})
    gwriter.write_log_to_gsheet(settings["GSHEET_TAB_NAME_LOGS"], unique_deals_with_relevant_fields, start_row = settings["GSHEET_LOG_FILE_START_ROW"])
    elapsed_time = time.time() - start_time
    gwriter.update_last_write(elapsed_time)
    print("Successfully updated information in {:.3f}.".format(elapsed_time))
    try:
        with open(LAST_RUN_SUCCESS_CACHE, "r"):
            pass
    except Exception:
        with open(LAST_RUN_SUCCESS_CACHE, "w"):
            su.send_success_message()

except Exception as e:
    if len(sys.argv) == 1:
        su.send_error_message(str(e))
        try:
            os.remove(LAST_RUN_SUCCESS_CACHE)
        except FileNotFoundError:
            pass
    print("Failed to update information.")
    raise
