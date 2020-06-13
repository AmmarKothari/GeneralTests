import csv
import hashlib
import multiprocessing
import multiprocessing.pool
import os
import pickle

import pdb
import time
from datetime import datetime
import functools

import yaml

from constants import gsheet_date_format, threeC_date_format
from helper_classes import MaxValueTracker

BOTS_FILENAME = 'bots.yaml'
LOG_FILENAMES = {'BOTINFO': 'bot_info.csv',
                 'DEAL_LOG': 'deal_log_{}.csv'}

MAX_DEALS_PER_REQUEST = 1000

DEAL_START_KEY = 'created_at'
DEAL_UPDATED_KEY = 'updated_at'
DEAL_END_KEY = 'closed_at'
CONVERT_TO_DATE_TIME = [DEAL_START_KEY, DEAL_UPDATED_KEY, DEAL_END_KEY]
MAX_SIMULTANEOUS_DEALS_KEY = 'max_simultaneous_deals'
MAX_COIN_IN_DEALS_KEY = 'max_coin_in_deals'
MAX_COIN_RESERVED_IN_DEALS_KEY = 'max_coin_reserved_in_deals'
MAX_SIMULTANEOUS_DEALS_SAME_BOT_KEY = 'max_simultaneous_same_bot_deals'

CACHED_DEALS_FN = 'cache_files/raw_bot_logs.p'
CACHE_LIFETIME_S = 600


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
    print('Fetching all deals')
    start = time.time()
    fetch_counter = 0
    while True:
        success, deals = cw.request(entity='deals', action='',
                                    payload={'limit': MAX_DEALS_PER_REQUEST, 'offset': offset})
        fetch_counter += 1
        _check_if_request_successful(success)
        all_deals.extend(deals)
        if len(deals) < MAX_DEALS_PER_REQUEST:
            break
        offset += MAX_DEALS_PER_REQUEST
    end = time.time()
    print('Done fetching {} deals in {:.3} s'.format(len(all_deals), end-start))
    return all_deals


def _cache_deals_to_file(all_deals):
    pickle.dump(all_deals, open(CACHED_DEALS_FN, 'wb'))


def _read_deals_from_cache():
    all_deals = pickle.load(open(CACHED_DEALS_FN, 'rb'))
    print('Loading deals from cache')
    return all_deals


def _cache_valid():
    is_valid = False
    try:
        if (time.time() - os.path.getmtime(CACHED_DEALS_FN)) < CACHE_LIFETIME_S:
            is_valid = True
    except FileNotFoundError:
        pass
    return is_valid


def get_data(cw, use_cache=False):
    cached_deals = _read_deals_from_cache()
    if use_cache and _cache_valid():
        all_deals = cached_deals
    else:
        all_deals = _get_all_deals(cw)
        # all_deals = cached_deals
        cached_deals = _update_date_format(cached_deals)
        all_deals = _update_date_format(all_deals)
        new_deals = _get_deals_that_need_update(all_deals, cached_deals)
        print('Total Deals to evaluate: {}'.format(len(new_deals)))
        new_deals = _calculate_duration(new_deals)
        new_deals = _calculate_all_max_simultaneous_open_deals(new_deals, all_deals)
        all_deals = _update_deals(new_deals, all_deals)
        # new_deals = _get_updated_and_new_deals(all_deals, cached_deals)
        # relevant_deals = _get_relevant_deals(all_deals, new_deals)
        # all_deals = _update_date_format(all_deals)
        # all_deals = _calculate_duration(all_deals)
        # all_deals = _calculate_all_max_simultaneous_open_deals(all_deals)
        _cache_deals_to_file(all_deals)
    return all_deals


def _update_deals(new_deals, all_deals):
    # sorted_deals = sorted(all_deals, key=lambda x: x[])
    for new_deal in new_deals:
        _update_deal(new_deal, all_deals)
    return all_deals


def _update_deal(new_deal, all_deals):
    for i, deal in enumerate(all_deals):
        if deal['id'] == new_deal['id']:
            all_deals[i] = new_deal
            return
    all_deals.append(new_deal)


def _get_deals_that_need_update(all_deals, cached_deals):
    """All deals that are new or have a new deal status since the last update."""

    # Get a dictionary of id: date
    cached_deals_info = {}
    for deal in cached_deals:
        cached_deals_info[deal['id']] = deal['updated_at']

    # Add deal indexes to set if deal id is not in keys or update time has changed
    updated_and_new_deals_idx = set()
    updated_and_new_deals = []
    for idx, deal in enumerate(all_deals):
        cached_deal_ids = list(cached_deals_info.keys())
        if deal['id'] in cached_deal_ids:
            if cached_deals_info[deal['id']] == deal['updated_at']:
                continue
        updated_and_new_deals.append(deal)
        updated_and_new_deals_idx.add(idx)
    print('New/Updated deals found: {}'.format(len(updated_and_new_deals_idx)))

    # Get all the deals that have a close date newer than the oldest created at date of new/updated deals.
    earliest_deal = sort_deals_by_key(updated_and_new_deals, 'created_at')[-1]
    sorted_all_deals = sort_deals_by_key(all_deals, 'closed_at')
    overlapping_deals = 0
    for idx, d in enumerate(sorted_all_deals):
        if d['closed_at'] and gsheet_time_to_datetime(d['closed_at']) >= gsheet_time_to_datetime(earliest_deal['created_at']):
            overlapping_deals += 1
            # print('Adding a deal that overlaps with an updated deal')
            updated_and_new_deals_idx.add(idx)
    print(f'Overlapping deals: {overlapping_deals}')
    need_updating = [all_deals[i] for i in updated_and_new_deals_idx]
    return need_updating


def _get_deal_hash(deal):
    return hashlib.sha256('{}{}'.format(deal['id'], deal['status'])).hexdigest()


def _get_updated_and_new_deals(all_deals, cached_deals):
    """All deals that are new or have a new deal status since the last update."""
    cached_deal_hashes = []
    pdb.set_trace()
    for deal in cached_deals:
        deal_hash = _get_deal_hash(deal)
        cached_deal_hashes.append(deal_hash)
    pdb.set_trace()
    relevant_deals = []
    for deal in all_deals:
        if _get_deal_hash(deal) in cached_deal_hashes:
            continue
        else:
            relevant_deals.append(deal)
    return relevant_deals



#       for deal, deal_hash in zip(all_deals, all_deals_has_set):
#           if cached_deal in cached_deals_has_set:
#               if deal == cached_deal:
#                   continue
#               new_deals.append(deal)
#     return new_deals

# def _get_relevant_deals(all_deals, new_deals):
"""All deals that need to updated.  (All deals still in bought phase + All new deals).
All other deals don't need to be updated."""




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


# ----------------
# Calculations
# ----------------
def threec_to_gsheet_time_format(threec_time):
    return datetime.strptime(threec_time, threeC_date_format).strftime(gsheet_date_format)


def gsheet_time_to_datetime(gsheet_time):
    return datetime.strptime(gsheet_time, gsheet_date_format)


def sort_deals_by_key(deals, key):
    def _sorter_helper(d):
        if d[key]:
            return datetime.strptime(d[key], gsheet_date_format)
        else:
            return datetime.utcnow()
    return sorted(deals, key=_sorter_helper, reverse=True)


def _update_date_format(all_deals):
    for deal in all_deals:
        for key in CONVERT_TO_DATE_TIME:
            if deal[key]:
                try:
                    deal[key] = threec_to_gsheet_time_format(deal[key])
                except ValueError:
                    # if the value has already been converted
                    pass
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


def _calculate_all_max_simultaneous_open_deals(new_deals, all_deals):
    print('Starting calculation for all max simultaneous deals')
    start_time = time.time()
    # calc_pool = multiprocessing.Pool(multiprocessing.cpu_count())
    calc_pool = multiprocessing.pool.ThreadPool(1)
    # TODO: all deals that have an end time after the earliest start time of a deal that changed needs to be updated
    all_deals = sorted(all_deals, key=lambda x: datetime.strptime(x['created_at'], gsheet_date_format), reverse=True)
    # all_deals = sorted(all_deals, key=lambda x: datetime.strptime(x['created_at'], gsheet_date_format), reverse=True)[:100]
    pool_func = functools.partial(_calculate_max_simultaneous_open_deals, all_deals=all_deals)
    result = calc_pool.map(pool_func, new_deals, chunksize=10)
    calc_pool.close()
    calc_pool.join()
    for deal, (max_simul, max_coin, max_reserved, max_simul_same) in zip(new_deals, result):
        deal[MAX_SIMULTANEOUS_DEALS_KEY] = max_simul
        deal[MAX_COIN_IN_DEALS_KEY] = max_coin
        deal[MAX_COIN_RESERVED_IN_DEALS_KEY] = max_reserved
        deal[MAX_SIMULTANEOUS_DEALS_SAME_BOT_KEY] = max_simul_same
    print('Total Elapsed Time: {:.3f}'.format(time.time() - start_time))
    return new_deals


def _calculate_max_simultaneous_open_deals(current_deal, all_deals):
    """Returns the number of transactions that are overlapping.

    Note: all_deals should already be sorted by created_at date
    """
    simultaneous_count = MaxValueTracker()
    coin_in_deals = MaxValueTracker()
    coin_reserved_in_deals = MaxValueTracker()
    simultaneous_same_bot_count = MaxValueTracker()
    overlap_deals = []
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
                                   overlap_deal[DEAL_END_KEY]):
                    new_overlap_deals.append(overlap_deal)
            overlap_deals = new_overlap_deals
            simultaneous_count.update_max_value(len(overlap_deals))
            for d in overlap_deals:
                # Failed to open deals have none for bought amount
                if d['bought_volume']:
                    coin_in_deals.add_current_value(float(d['bought_volume']))
                    coin_reserved_in_deals.add_current_value(float(d['reserved_base_coin']))
                if deal['bot_id'] == d['bot_id']:
                    simultaneous_same_bot_count.add_current_value(1)
            coin_in_deals.update_max_value(reset=True)
            coin_reserved_in_deals.update_max_value(reset=True)
            simultaneous_same_bot_count.update_max_value(reset=True)
    return simultaneous_count.max_value, coin_in_deals.max_value, coin_reserved_in_deals.max_value, \
           simultaneous_same_bot_count.max_value


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
    now = datetime.utcnow().strftime(gsheet_date_format)
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
