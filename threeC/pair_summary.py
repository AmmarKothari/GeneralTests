import configparser
import collections

import pdb
import yaml
from py3cw import request as cw_req

import account_info as account_info_module
import bot_info
import deal_handlers

config = configparser.ConfigParser()
config.read("config_files/config.ini")

OPEN_TRADE_DURATION_STEP = 5*60*60


class PairSummary:
    def __init__(self):
        self.id = ''
        self.count = 0
        self.durations = list()
        self.bot_ids_with_open_trades = list()
        self.bot_ids_that_can_trade = list()
        self.total_deals = 0

    def should_open_new_bot(self):
        # TODO: Check number of simultaneous deals for each bot?
        # This isn't right.  Need to check bots that could make this trade.
        if self.count >= len(self.bot_ids_with_open_trades):
            shortest_duration = min(self.durations)
            if shortest_duration > OPEN_TRADE_DURATION_STEP:
                return True
        return False

    def too_many_bots(self):
        if self.count < len(self.bot_ids_with_open_trades):
            return True

    @property
    def remaining_trades(self):
        return self.total_deals - self.count

    def __repr__(self):
        return f"{self.id}: {self.count} on bots {self.bot_ids_with_open_trades}. Max trades: {self.total_deals}. Remaining trades: {self.remaining_trades}"


with open("config_files/settings.yaml") as settings_f:
    settings = yaml.load(settings_f, Loader=yaml.Loader)


py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])
account_info = account_info_module.AccountInfo(py3cw, real=True)
bots_info = bot_info.BotInfo(py3cw)

deal_handler = deal_handlers.DealHandler(py3cw)

open_deals = deal_handler.deal_cacher.open_deals
deal_summary = collections.defaultdict(PairSummary)


for deal in open_deals:
    base_id, pair_id = deal['pair'].split('_')
    # TODO: Don't hardcode base pair
    if base_id == 'BTC':
        deal_summary[pair_id].id = pair_id
        deal_summary[pair_id].count += 1
        deal_summary[pair_id].durations.append(deal['duration'])
        if deal['id'] not in deal_summary[pair_id].bot_ids_with_open_trades:
            deal_summary[pair_id].bot_ids_with_open_trades.append(deal['id'])
        deal_summary[pair_id].durations.sort()

for bot in bots_info.bots:
    for pair in bot['pairs']:
        base_id, alt_id = pair.split('_')

        if alt_id in deal_summary.keys():
            deal_summary[alt_id].bot_ids_that_can_trade.append(bot['id'])
            deal_summary[alt_id].total_deals += bot['allowed_deals_on_same_pair']
print([d.remaining_trades for d in deal_summary.values()])
pdb.set_trace()


# For each pair:
for pair in deal_summary.values():
    # If a new spot is needed, open a new trade.
    if pair.should_open_new_bot():
        print(f'Should open pair on new bot for {pair.id}')
        # TODO: add to a new bot
    # If no trade should be opened, close all bots that have open slots
    # elif pair.too_many_bots(num_bots):
    #     print(f'Need to add bot for {pair.id}')
    # If there is one open spot, and a trade should be opened, don't do anything.
    else:
        print(f'Dont need to do anything for {pair.id}')
    # TODO: remove when more than one bot can open a deal









pdb.set_trace()

