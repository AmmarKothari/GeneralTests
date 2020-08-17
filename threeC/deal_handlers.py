import functools
from datetime import datetime

import constants
import time_converters
from api_deal_handler import APIDealHandler
from constants import DEAL_UPDATED_KEY, DEAL_START_KEY, DEAL_END_KEY
from deal_cacher import DealCacher
from threeCDataGetter import _calculate_all_max_simultaneous_open_deals
from time_converters import gsheet_time_to_datetime

CACHED_DEALS_FN = 'cache_files/raw_bot_logs.p'


def get_data(cw, use_cache=False):
    deal_handler = DealHandler(cw)
    deal_handler.use_cache_deals()

    # If the cached deals is valid, return those so computation takes less time.  Mostly for debugging.
    if not (use_cache and deal_handler.deal_cacher.cache_valid()):
        deal_handler.fetch_deals()
        need_updating = deal_handler.get_deals_that_need_updating()
        need_updating = _calculate_duration(need_updating)
        new_deals = _calculate_all_max_simultaneous_open_deals(need_updating, deal_handler.api_deals)
        deal_handler.update_deals(new_deals)
        deal_handler.cache_deals_to_file()
    return deal_handler.all_deals


class Deal:
    def __init__(self, deal):
        self.deal = deal

    def get_created_at(self):
        return time_converters.gsheet_time_to_datetime(self.deal[constants.DEAL_START_KEY])

    def get_updated_at(self):
        return time_converters.gsheet_time_to_datetime(self.deal[constants.DEAL_UPDATED_KEY])

    def get_closed_at(self):
        if self.deal[constants.DEAL_END_KEY]:
            return time_converters.gsheet_time_to_datetime(self.deal[constants.DEAL_END_KEY])
        else:
            return datetime.utcnow()

    def get_base_currency(self):
        return self.deal['from_currency']

    def get_alt_currency(self):
        return self.deal['to_currency']

    def is_valid_trade(self):
        return self.deal['status'] != 'failed'

    def __repr__(self):
        return f'Base: {self.get_base_currency()} Alt: {self.get_alt_currency()}'


class DealHandler:
    def __init__(self, cw):
        self.cw = cw
        self.all_deals = []
        self.api_deals = []
        self.deal_cacher = DealCacher(CACHED_DEALS_FN)

    def fetch_deals(self):
        self.api_deals = APIDealHandler(self.cw).get_all_deals()

    def use_cache_deals(self):
        self.all_deals = self.deal_cacher.cached_deals

    def cache_deals_to_file(self):
        self.deal_cacher.cache_deals_to_file(self.all_deals)

    @functools.lru_cache()
    def get_deals_that_need_updating(self):
        """Deals that have a changed compared to cache or are new deals."""
        # Add deal indexes to set if deal id is not in keys or update time has changed
        updated_and_new_deals_idx = set()
        updated_and_new_deals = []
        for idx, deal in enumerate(self.api_deals):
            if deal['id'] in self.deal_cacher.cached_deal_ids:
                if self.deal_cacher.cached_deals_info[deal['id']] == deal[DEAL_UPDATED_KEY]:
                    continue
            updated_and_new_deals.append(deal)
            updated_and_new_deals_idx.add(idx)
        print('New/Updated deals found: {}'.format(len(updated_and_new_deals_idx)))

        need_updating = []
        if updated_and_new_deals:
            # Get all the deals that have a close date newer than the oldest created at date of new/updated deals.
            earliest_deal = sort_deals_by_key(updated_and_new_deals, DEAL_START_KEY)[-1]
            sorted_all_deals = sort_deals_by_key(self.api_deals, DEAL_END_KEY)
            overlapping_deals = 0
            for idx, d in enumerate(sorted_all_deals):
                if not d[DEAL_END_KEY] or gsheet_time_to_datetime(d[DEAL_END_KEY]) >= gsheet_time_to_datetime(
                        earliest_deal[DEAL_START_KEY]):
                    overlapping_deals += 1
                    updated_and_new_deals_idx.add(idx)
            print(f'Overlapping deals: {overlapping_deals}')
            need_updating = [self.api_deals[i] for i in updated_and_new_deals_idx]
            print(f'Total Deals to evaluate: {len(need_updating)}')
        return need_updating

    def update_deals(self, new_deals):
        for new_deal in new_deals:
            self._update_deal(new_deal)
        self.all_deals = sort_deals_by_key(self.all_deals, DEAL_START_KEY)

    def _update_deal(self, new_deal):
        for i, deal in enumerate(self.all_deals):
            if deal['id'] == new_deal['id']:
                self.all_deals[i] = new_deal
                return
        self.all_deals.append(new_deal)


def sort_deals_by_key(deals, key):
    def _sorter_helper(d):
        if d[key]:
            return gsheet_time_to_datetime(d[key])
        else:
            return datetime.utcnow()
    return sorted(deals, key=_sorter_helper, reverse=True)


def _calculate_duration(deals):
    """Calculation duration of each deal"""
    for deal in deals:
        if deal[DEAL_END_KEY]:
            end_time = gsheet_time_to_datetime(deal[DEAL_END_KEY])
        else:
            end_time = datetime.utcnow()

        duration = end_time - gsheet_time_to_datetime(deal[DEAL_START_KEY])
        duration = duration.total_seconds()
        deal['duration'] = duration
    return deals
