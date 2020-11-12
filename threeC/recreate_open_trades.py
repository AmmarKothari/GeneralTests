import configparser
import datetime

from py3cw import request as cw_req

import constants
import deal_handlers
from bot_info import BotInfo
from deal_handlers import DealHandler, Deal
import collections

class CurrencyInfo:
    def __init__(self):
        # self.currency = currency
        self.durations = []
        self.ids = []

    def get_count(self):
        return len(self.durations)

    def __repr__(self):
        return f'ID: {self.ids} Count: {self.get_count()}'


class Bot:
    def __init__(self, bot):
        self._bot_dict = bot
        self.deals = []

    @property
    def id(self):
        return self._bot_dict['id']

    @property
    def pairs(self):
        return [p.split('_')[1] for p in self._bot_dict['pairs']]

    @property
    def allowed_deals(self):
        return self._bot_dict['allowed_deals_on_same_pair']

    def add_deal(self, deal):
        # Should not ever have to update info in the deal list
        if deal.get_id() not in self.get_deal_ids():
            self.deals.append(deal)

    def get_deal_ids(self):
        return [deal.get_id() for deal in self.deals]

    def available_deals_for_pair(self, alt_coin):
        open_deals_count = len([d for d in self.deals if d.get_alt_currency() == alt_coin])
        return self.allowed_deals - open_deals_count


class Bots:
    def __init__(self, bot_info):
        self.bots = {b['id']: Bot(b) for b in bot_info.bots}

    def add_deal(self, deal):
        # There are old bots that no longer exist i think
        if deal.get_id() in self.get_bot_ids():
            self.bots[deal.get_bot_id()].add_deal(deal)

    def get_bot_ids(self):
        return self.bots.keys()


class NewDealAvailability:
    def __init__(self, bot_info):
        self.bots = [Bot(bot) for bot in bot_info.bots]


NEW_DEAL_THRESHOLD = 24 * 60 * 60

config = configparser.ConfigParser()
config.read("config_files/config.ini")

py3cw = cw_req.Py3CW(key=config['threeC']['key'], secret=config['threeC']['secret'])


deal_handler = DealHandler(py3cw)

# TODO: Change this to false when done developing
data = deal_handlers.get_data(py3cw, use_cache=True)


# Do i need to filter these deals based on being not failed?
oldest_deal = Deal(deal_handlers.sort_deals_by_key(data, constants.DEAL_START_KEY)[-1])
most_recent_deal = Deal(deal_handlers.sort_deals_by_key(data, constants.DEAL_END_KEY)[0])

era_start = oldest_deal.get_created_at()

era_end = most_recent_deal.get_closed_at()

# Convert all the deal dicts into classes so they are easier to work with.
# Filter out the things we don't want
all_deals = []
for deal_def in deal_handlers.sort_deals_by_key(data, constants.DEAL_START_KEY):
    deal = Deal(deal_def)
    if deal.get_base_currency() != 'BTC':
        continue
    if not deal.is_valid_trade():
        continue
    all_deals.append(Deal(deal_def))
all_deals.reverse()

bot_info = BotInfo(py3cw)

current_time = era_start.replace(minute=0, second=0, microsecond=0)
while current_time < era_end:
    # print(current_time)
    deals_open_at_current_time = []
    for deal in all_deals:
        # This deal was closed before the time of interest so just short circuit
        if deal.get_closed_at() < current_time:
            continue
        if deal.get_created_at() <= current_time <= deal.get_closed_at():
            deals_open_at_current_time.append(deal)

        # At the point in the list where the deals were opened after the time of interest so move on
        if deal.get_created_at() > current_time:
            break

    # From here down would be what runs every hour
    if deals_open_at_current_time:
        bot_list = Bots(bot_info)
        deal_num_tracker = collections.defaultdict(CurrencyInfo)
        for deal in deals_open_at_current_time:
            bot_list.add_deal(deal)
            deal_num_tracker[deal.get_alt_currency()].durations.append(current_time - deal.get_created_at())
            deal_num_tracker[deal.get_alt_currency()].ids.append(deal.get_id())
        for currency, currency_info in deal_num_tracker.items():
            # print(f'\t Currency: {currency:5} Count: {currency_info.get_count()}  Min Duration: {min(currency_info.durations)}')

            if min(currency_info.durations).total_seconds() > NEW_DEAL_THRESHOLD:
                # There are old bots that no longer exist i think
                if deal.get_id() not in bot_list.get_bot_ids():
                    continue
                available_deals_for_pair = bot_list.bots[deal.get_id()].available_deals_for_pair(deal.get_alt_currency())
                # TODO: make this a func of bot_list
                if available_deals_for_pair > 1:
                    # TODO: This should be checked on every set not just on the ones whose threshold has crossed.
                    print("Too many slots open. Close one")
                elif available_deals_for_pair == 1:
                    print("Perfect number of open slots")
                elif available_deals_for_pair < 1:
                    print("Need to open a new slot")
                else:
                    print("i don't know how i got here")
                    import pdb; pdb.set_trace()
    current_time = current_time + datetime.timedelta(hours=1)


import pdb; pdb.set_trace()