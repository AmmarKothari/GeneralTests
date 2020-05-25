import pdb
from py3cw import request as cw_req
import configparser
import os
import yaml

import constants
import gsheet_writer

import threeCDataGetter as tcdg
from slack_updater import SlackUpdater

config = configparser.ConfigParser()
config.read("config.ini")

with open("settings.yaml") as settings_f:
	settings = yaml.load(settings_f, Loader=yaml.Loader)

py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])

try:
	data = tcdg.get_data(py3cw)
	bots = tcdg.get_bots(py3cw)
	gwriter = gsheet_writer.GSheetWriter(os.path.expanduser(settings['GSHEET_SERVICE_FILE']), py3cw, settings['GSHEET_LOG_FILE'])

	gwriter.write_account_stats(settings['GSHEET_TAB_NAME_ACCOUNT_VALUE'], constants.MAIN_ACCOUNT_KEY)
	gwriter.write_bot_id_to_names_map_to_gsheet(bots, settings['GSHEET_TAB_NAME_BOT_IDS'])

	filtered_deals = []
	for bot_group_key in settings['bot_groups']:
		for bot_id in settings['bot_groups'][bot_group_key]:
			bot_deals = tcdg.filter_by_bot_id(data, bot_id)
			for deal in bot_deals:
				deal['bot_group'] = bot_group_key
			filtered_deals.extend(bot_deals)
	filtered_deals = sorted(filtered_deals, key=lambda x: int(x['id']), reverse=True)
	gwriter.write_log_to_gsheet(settings['GSHEET_TAB_NAME'], filtered_deals)
	gwriter.update_last_write()

except Exception:
	su = SlackUpdater(config['threeC']['slack_bot_token'])
	su.send_error_message()
	raise
