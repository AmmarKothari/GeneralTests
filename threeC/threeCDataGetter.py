import csv
import pdb
import time
from datetime import datetime
import functools

import yaml

from constants import gsheet_date_format, threeC_date_format

BOTS_FILENAME = 'bots.yaml'
LOG_FILENAMES = {'BOTINFO': 'bot_info.csv',
                 'DEAL_LOG': 'deal_log_{}.csv'}

MAX_DEALS_PER_REQUEST = 1000

DEAL_START_KEY = 'created_at'
DEAL_END_KEY = 'updated_at'
CONVERT_TO_DATE_TIME = [DEAL_START_KEY, DEAL_END_KEY, 'closed_at']
MAX_SIMULTANEOUS_DEALS_KEY = 'max_simultaneous_deals'
MAX_COIN_IN_DEALS_KEY = 'max_coin_in_deals'


# ----------------
# Getting Data
# ----------------

def _load_yaml():
    with open(BOTS_FILENAME) as bot_yaml:
        settings_dict = yaml.load(bot_yaml)
    return settings_dict


def _check_if_request_successful(success):
    if success:
        raise Exception('Failed to get data')


def get_bots(cw):
    success, bots = cw.request(entity='bots', action='')
    _check_if_request_successful(success)
    return bots


def _get_all_deals(cw):
    all_deals = []
    offset = 0
    while True:
        success, deals = cw.request(entity='deals', action='',
                                    payload={'limit': MAX_DEALS_PER_REQUEST, 'offset': offset})
        _check_if_request_successful(success)
        all_deals.extend(deals)
        if len(deals) < MAX_DEALS_PER_REQUEST:
            break
        offset += MAX_DEALS_PER_REQUEST
    return all_deals


def get_data(cw):
    all_deals = _get_all_deals(cw)
    all_deals = _update_date_format(all_deals)
    all_deals = _calculate_duration(all_deals)
    all_deals = _calculate_all_max_simultaneous_open_deals(all_deals)
    return all_deals


def filter_by_bot_id(deals, bot_id):
    if not deals:
        return []
    filtered_deals = []
    for deal in deals:
        if deal['bot_id'] == bot_id:
            filtered_deals.append(deal)
        else:
            pass
    return filtered_deals


def get_deals(filtered_deals):
    completed_deals = []
    ongoing_deals = []
    for deal in filtered_deals:
        if deal['finished?']:
            completed_deals.append(deal)
        else:
            ongoing_deals.append(deal)
    return completed_deals, ongoing_deals


class BotInfo:
    def __init__(self, cw, account_id):
        self.account_id = account_id
        self.cw = cw

    @property
    @functools.lru_cache()
    def strategy_list(self):
        success, response = self.cw.request(entity='bots', action='strategy_list', payload={'account_id': self.account_id})
        _check_if_request_successful(success)
        return response.keys()

    def get_strategy(self, strategy_name):
        return self.strategy_list[strategy_name]


class AccountInfo:
    def __init__(self, cw):
        self.cw = cw

    @property
    @functools.lru_cache()
    def accounts(self):
        success, accounts = self.cw.request(entity='accounts', action='')
        _check_if_request_successful(success)
        return accounts

    @property
    @functools.lru_cache()
    def account_ids(self):
        account_ids = {}
        for account in self.accounts:
            account_ids[account['exchange_name']] = account['id']
        return account_ids

    def get_account_balance(self, account_id):
        for account in self.accounts:
            if account['id'] == account_id:
                return float(account['btc_amount'])

    def get_account_profit(self, account_id):
        for account in self.accounts:
            if account['id'] == account_id:
                return float(account['day_profit_btc'])


# ----------------
# Calculations
# ----------------

def _update_date_format(all_deals):
    for deal in all_deals:
        for key in CONVERT_TO_DATE_TIME:
            if deal[key]:
                deal[key] = datetime.strptime(deal[key], threeC_date_format).strftime(gsheet_date_format)
                if 'T' in deal[key]:
                    raise Exception('Failed to convert to proper date format.')
            else:
                deal[key] = None
    return all_deals


def _calculate_duration(all_deals):
    for deal in all_deals:
        if deal[CONVERT_TO_DATE_TIME[2]]:
            end_time = datetime.strptime(deal[CONVERT_TO_DATE_TIME[2]], gsheet_date_format)
        else:
            end_time = datetime.utcnow()

        duration = end_time - datetime.strptime(deal[CONVERT_TO_DATE_TIME[0]], gsheet_date_format)
        duration = duration.total_seconds()
        deal['duration'] = duration
    return all_deals


def _calculate_all_max_simultaneous_open_deals(all_deals):
    count = 0
    for deal in all_deals:
        deal[MAX_SIMULTANEOUS_DEALS_KEY], deal[MAX_COIN_IN_DEALS_KEY] = _calculate_max_simultaneous_open_deals(deal, all_deals)
        count += 1
        # print('Count of deals analyzed: {}'.format(count))
    return all_deals


def _calculate_max_simultaneous_open_deals(current_deal, all_deals):
    """Returns the number of transactions that are overlapping."""
    max_simultaneous_count = 0
    max_coin_in_deals = 0
    overlap_deals = []
    all_deals = sorted(all_deals, key=lambda x: datetime.strptime(x['created_at'], gsheet_date_format), reverse=True)
    for deal in all_deals:
        if deal['from_currency'] != current_deal['from_currency']:
            continue
        is_overlapping = _is_overlapping(deal[DEAL_START_KEY], deal[DEAL_END_KEY], current_deal[DEAL_START_KEY],
                                         current_deal[DEAL_END_KEY])
        if is_overlapping:
            overlap_deals.append(deal)
            new_overlap_deals = []
            for overlap_deal in overlap_deals:
                if _is_overlapping(deal[DEAL_START_KEY], deal[DEAL_END_KEY], overlap_deal[DEAL_START_KEY],
                                   overlap_deal[DEAL_START_KEY]):
                    new_overlap_deals.append(overlap_deal)
            overlap_deals = new_overlap_deals
            max_simultaneous_count = max(max_simultaneous_count, len(overlap_deals))
            current_max_coin = 0
            for d in overlap_deals:
                # Failed to open deals have none for bought amount
                if d['bought_volume']:
                    current_max_coin += float(d['bought_volume'])
            max_coin_in_deals = max(max_coin_in_deals, current_max_coin)
    return max_simultaneous_count, max_coin_in_deals


def _is_overlapping(start_1, end_1, start_2, end_2):
    is_overlapping = False
    #  Scenario 1
    #   |-------|
    #        |-----|
    #  Scenario 2
    #  |------------|
    #     |-----|
    if not start_1 or not start_2:
        return False
    now = datetime.utcnow()
    end_1 = end_1 or now
    end_2 = end_2 or now

    start_1 = datetime.strptime(start_1, gsheet_date_format)
    start_2 = datetime.strptime(start_2, gsheet_date_format)
    end_1 = datetime.strptime(end_1, gsheet_date_format)
    end_2 = datetime.strptime(end_2, gsheet_date_format)
    if (start_2 >= start_1 and start_2 <= end_1):
        is_overlapping = True
    #  Scenario 3
    #       |------|
    #  |-------|
    #  Scenario 4
    #         |------|
    #  |------------------|
    elif start_1 >= start_2 and start_1 <= end_2:
        is_overlapping = True
    return is_overlapping


# ----------------
# Logging
# ----------------

def write_bot_info_to_log(cw):
    bots = get_bots(cw)
    header = bots[0].keys()
    with open(LOG_FILENAMES['BOTINFO'], 'w') as bot_f:
        dict_writer = csv.DictWriter(bot_f, header)
        dict_writer.writeheader()
        dict_writer.writerows(bots)


def print_bot_id_to_name_mapping(cw):
    bots = get_bots(cw)
    for bot in bots:
        print('{} -> {}'.format(bot['id'], bot['name']))


def get_name_from_id(cw, id):
    bots = get_bots(cw)
    for bot in bots:
        if bot['id'] == id:
            return bot['name']
    raise Exception('No bot found with that id')


def write_log_with_deals(bot_id, deals):
    # TDOO: Need to deal with deals that were not completed but now are
    # Could rewrite whole file or find a way to replace just that row in file.
    log_filename = LOG_FILENAMES['DEAL_LOG'].format(bot_id)
    header = deals[0].keys()

    # previously_logged_deals = []
    # write_mode = 'a'
    # try:
    # 	with open(log_filename, 'r') as deal_log_f:
    # 		reader = csv.DictReader(deal_log_f)
    # 		for deal in reader:
    # 			previously_logged_deals.append(int(deal['id']))
    # except FileNotFoundError:
    # 	write_mode = 'w'
    # 	print('File not found.  Creating new file.')

    # Rewrite the log file everytime
    write_mode = 'w'
    with open(log_filename, write_mode) as deal_log_f:
        dict_writer = csv.DictWriter(deal_log_f, header)
        if write_mode == 'w':
            dict_writer.writeheader()
        for deal in deals:
            # if deal['id'] not in previously_logged_deals:
            # print('Logging new deal')
            dict_writer.writerow(deal)

# def test_setup_bot(cw, bot_name):
# 	settings_dict = _load_yaml()
# 	# settings_dict['base_keiko']['strategy_list'] = [get_strategy(cw, 'keiko')]
# 	success, response = cw.request(entity='bots', action='create_bot', payload=settings_dict['base_keiko'])
# 	pdb.set_trace()
# 	return response

# def test_update_bot(cw, bot_name):
# 	settings_dict = _load_yaml()[bot_name]
# 	# if settings_dict['is_update']:
# 	settings_dict.pop('is_update')
# 	success, response = cw.request(entity='bots', action='update', action_id=str(settings_dict['id']), payload=settings_dict)
# 	pdb.set_trace()


# bots = get_bots(py3cw)
# data = get_data(py3cw)
# filtered_deals = filter_by_bot_id(data, MAIN_BOT_ID)
# completed_deals, ongoing_deals = get_deals(filtered_deals)
# max_open_duration = get_longest_open_deal(ongoing_deals)
# print('Longest open deal {:.3f}'.format(max_open_duration))

# write_bot_info_to_log(py3cw)
# print_bot_id_to_name_mapping(py3cw)
