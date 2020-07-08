import datetime
import time

import pdb
import sys
from py3cw import request as cw_req
import configparser
import os
import yaml

import constants
import deal_handlers
import gsheet_writer

import threeCDataGetter as tcdg
from bot_info import BotInfo
from constants import LAST_RUN_SUCCESS_CACHE
from deal_handlers import DealHandler
from slack_updater import SlackUpdater


config = configparser.ConfigParser()
config.read("config_files/config.ini")

with open("config_files/settings.yaml") as settings_f:
	settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])

su = SlackUpdater(config['threeC']['slack_bot_token'])

try:
	print("Starting calculation at {}".format(datetime.datetime.now().strftime("%D - %H:%M")))
	# TODO: Add a singleton class here to avoid this from being run multiple times simultaneously on cloud instance.
	start_time = time.time()
	gwriter = gsheet_writer.GSheetWriter(os.path.expanduser(settings['GSHEET_SERVICE_FILE']), py3cw,
										 settings['GSHEET_LOG_FILE'])
	gwriter.write_account_stats(settings['GSHEET_TAB_NAME_ACCOUNT_VALUE'], constants.MAIN_ACCOUNT_KEY)
	bot_info = BotInfo(py3cw)
	gwriter.write_bot_id_to_names_map_to_gsheet(bot_info.bots, settings['GSHEET_TAB_NAME_BOT_IDS'])

	deal_handler = DealHandler(py3cw)
	data = deal_handlers.get_data(py3cw, use_cache=False)

	filtered_deals = []
	for bot_group_key in settings['bot_groups']:
		for bot_id in settings['bot_groups'][bot_group_key]:
			bot_deals = tcdg.filter_by_bot_id(data, bot_id)
			for deal in bot_deals:
				deal['bot_group'] = bot_group_key
			filtered_deals.extend(bot_deals)
	filtered_deals = sorted(filtered_deals, key=lambda x: int(x['id']), reverse=True)
	gwriter.write_log_to_gsheet(settings['GSHEET_TAB_NAME_LOGS'], filtered_deals)
	elapsed_time = time.time() - start_time
	gwriter.update_last_write(elapsed_time)
	print('Successfully updated information in {:.3f}.'.format(elapsed_time))
	try:
		with open(LAST_RUN_SUCCESS_CACHE, 'r'):
			pass
	except Exception:
		with open(LAST_RUN_SUCCESS_CACHE, 'w'):
			su.send_success_message()

except Exception:
	if len(sys.argv) == 1:
		su.send_error_message()
		try:
			os.remove(LAST_RUN_SUCCESS_CACHE)
		except FileNotFoundError:
			pass
	print('Failed to update information.')
	raise
