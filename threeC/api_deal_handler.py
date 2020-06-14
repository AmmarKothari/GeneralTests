from datetime import datetime
import time

from constants import CONVERT_TO_DATE_TIME, gsheet_date_format, threeC_date_format
from request_helper import _check_if_request_successful

MAX_DEALS_PER_REQUEST = 100


class APIDealHandler:
    def __init__(self, cw):
        self.cw = cw
        self.all_deals = []

    def get_all_deals(self):
        """Get all deals from API"""
        print('Fetching all deals')
        start = time.time()
        offset = 0
        fetch_counter = 0
        # Keep requesting until return fewer than maximum number of deals
        while True:
            success, deals = self.cw.request(entity='deals', action='',
                                             payload={'limit': MAX_DEALS_PER_REQUEST, 'offset': offset})
            fetch_counter += 1
            _check_if_request_successful(success)
            self.all_deals.extend(deals)
            if len(deals) < MAX_DEALS_PER_REQUEST:
                break
            offset += MAX_DEALS_PER_REQUEST
        end = time.time()
        print('Done fetching {} deals in {:.3} s'.format(self.num_deals, end - start))
        # TODO: Convert to datetime
        self._update_date_format()
        return self.all_deals

    @property
    def num_deals(self):
        return len(self.all_deals)

    def _update_date_format(self):
        """Update all the times to match google sheet format."""
        for deal in self.all_deals:
            for key in CONVERT_TO_DATE_TIME:
                if deal[key]:
                    try:
                        deal[key] = _threec_to_gsheet_time_format(deal[key])
                    except ValueError:
                        # if the value has already been converted
                        pass
                    if 'T' in deal[key]:
                        raise Exception('Failed to convert to proper date format.')
                else:
                    deal[key] = None
        return self.all_deals


def _threec_to_gsheet_time_format(threec_time):
    return datetime.strptime(threec_time, threeC_date_format).strftime(gsheet_date_format)
