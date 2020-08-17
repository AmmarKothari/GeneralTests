import configparser
import datetime

from py3cw import request as cw_req

import constants
import deal_handlers
from deal_handlers import DealHandler, Deal
import collections

class CurrencyInfo:
    def __init__(self):
        # self.currency = currency
        self.count = 0
        self.durations = []

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

current_time = era_start.replace(minute=0, second=0, microsecond=0)
while current_time < era_end:
    print(current_time)
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
    if deals_open_at_current_time:
        deal_num_tracker = collections.defaultdict(CurrencyInfo)
        for deal in deals_open_at_current_time:
            deal_num_tracker[deal.get_alt_currency()].count += 1
            deal_num_tracker[deal.get_alt_currency()].durations.append(current_time - deal.get_created_at())
        for currency, currency_info in deal_num_tracker.items():
            print(f'\t Currency: {currency:5} Count: {currency_info.count}  Min Duration: {min(currency_info.durations)}')
    current_time = current_time + datetime.timedelta(hours=1)


import pdb; pdb.set_trace()