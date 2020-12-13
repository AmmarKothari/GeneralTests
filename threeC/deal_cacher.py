import functools
import os
import pickle
import time

from constants import DEAL_UPDATED_KEY


CACHE_LIFETIME_S = 6000


class DealCacher:
    """Handles cached deals."""

    def __init__(self, cache_fn: str, cache_timeout: float = CACHE_LIFETIME_S):
        self.cache_fn = cache_fn
        self._cache_timeout = cache_timeout

    def cache_deals_to_file(self, all_deals):
        pickle.dump(all_deals, open(self.cache_fn, "wb"))

    def _get_cached_deals_from_file(self):
        return pickle.load(open(self.cache_fn, "rb"))

    def cache_valid(self):
        is_valid = False
        try:
            if (time.time() - os.path.getmtime(self.cache_fn)) < self._cache_timeout:
                is_valid = True
        except FileNotFoundError:
            pass
        return is_valid

    @property
    def cached_deals(self):
        try:
            return self._get_cached_deals_from_file()
        except FileNotFoundError:
            print("No cache file found.")
            return []

    @property
    def cached_deals_info(self):
        # Get a dictionary of id: date
        cached_deals_info = {}
        for deal in self.cached_deals:
            cached_deals_info[deal["id"]] = deal[DEAL_UPDATED_KEY]
        return cached_deals_info

    @property
    def cached_deal_ids(self):
        return list(self.cached_deals_info.keys())

    @property
    def open_deals(self):
        open_deals = []
        for deal in self.cached_deals:
            if deal["status"] == "bought":
                open_deals.append(deal)
        return open_deals
