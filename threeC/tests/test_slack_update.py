import configparser

from slack_updater import SlackUpdater

config = configparser.ConfigParser()
# TODO: Fix this file location
config.read("config.ini")

su = SlackUpdater(config['threeC']['slack_bot_token'])
su.send_error_message()






