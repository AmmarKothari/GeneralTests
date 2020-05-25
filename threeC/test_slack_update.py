import configparser

import pdb
import slack

from slack_updater import SlackUpdater


config = configparser.ConfigParser()
config.read("config.ini")

su = SlackUpdater(config['threeC']['slack_bot_token'])
su.send_error_message()






