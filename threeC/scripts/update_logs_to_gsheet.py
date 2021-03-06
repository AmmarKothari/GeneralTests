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

    account_info = account_info_module.AccountInfo(py3cw, real=True)
    account_stats = account_info.get_account_stats(settings["MAIN_ACCOUNT_KEY"])
    gwriter.write_account_stats(
        settings["GSHEET_TAB_NAME_ACCOUNT_VALUE"], account_stats
    )
    bot_info = BotInfo(py3cw)

    # TODO: Clear sheet before writing
    gwriter.write_bot_id_to_names_map_to_gsheet(
        bot_info.bots, settings["GSHEET_TAB_NAME_BOT_IDS"]
    )
    deal_handler = DealHandler(py3cw)
    data = deal_handlers.get_data(py3cw, use_cache=False)

    filtered_deals = []
    for bot_group_key in settings["bot_groups"]:
        for bot_id in settings["bot_groups"][bot_group_key]:
            bot_deals = tcdg.filter_by_bot_id(data, bot_id)
            for deal in bot_deals:
                deal["bot_group"] = bot_group_key
            filtered_deals.extend(bot_deals)
    unique_deals = []
    unique_deal_ids = []
    for deal in filtered_deals:
        if deal["id"] not in unique_deal_ids:
            unique_deal_ids.append(deal["id"])
            unique_deals.append(deal)
    unique_deals = sorted(unique_deals, key=lambda x: int(x["id"]), reverse=True)
    gwriter.write_log_to_gsheet(settings["GSHEET_TAB_NAME_LOGS"], unique_deals)
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
