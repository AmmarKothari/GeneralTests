import csv
import functools
import hashlib
import multiprocessing
import multiprocessing.pool
import time
from datetime import datetime
import tqdm

import pdb

from bot_info import BotInfo
from constants import (
    gsheet_date_format,
    threeC_date_format,
    DEAL_START_KEY,
    DEAL_END_KEY,
)
from time_converters import gsheet_time_to_datetime
from helper_classes import MaxValueTracker

LOG_FILENAMES = {"BOTINFO": "bot_info.csv", "DEAL_LOG": "deal_log_{}.csv"}

MAX_SIMULTANEOUS_DEALS_KEY = "max_simultaneous_deals"
MAX_COIN_IN_DEALS_KEY = "max_coin_in_deals"
MAX_COIN_RESERVED_IN_DEALS_KEY = "max_coin_reserved_in_deals"
MAX_SIMULTANEOUS_DEALS_SAME_BOT_KEY = "max_simultaneous_same_bot_deals"


# ----------------
# Getting Data
# ----------------


def _get_deal_hash(deal):
    return hashlib.sha256("{}{}".format(deal["id"], deal["status"])).hexdigest()


def _get_updated_and_new_deals(all_deals, cached_deals):
    """All deals that are new or have a new deal status since the last update."""
    cached_deal_hashes = []
    for deal in cached_deals:
        deal_hash = _get_deal_hash(deal)
        cached_deal_hashes.append(deal_hash)
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
        if deal["bot_id"] == bot_id:
            filtered_deals.append(deal)
        else:
            pass
    return filtered_deals


def get_deals(filtered_deals):
    completed_deals = []
    ongoing_deals = []
    for deal in filtered_deals:
        if deal["finished?"]:
            completed_deals.append(deal)
        else:
            ongoing_deals.append(deal)
    return completed_deals, ongoing_deals


# ----------------
# Calculations
# ----------------


def _calculate_all_max_simultaneous_open_deals(new_deals, all_deals, skip_calc=False):
    print("Starting calculation for all max simultaneous deals")
    start_time = time.time()
    if not skip_calc:
        calc_pool = multiprocessing.Pool(multiprocessing.cpu_count())
        # calc_pool = multiprocessing.pool.ThreadPool(1)
        all_deals = sorted(
            all_deals,
            key=lambda x: datetime.strptime(x["created_at"], gsheet_date_format),
            reverse=True,
        )
        pool_func = functools.partial(
            _calculate_max_simultaneous_open_deals, all_deals=all_deals
        )
        result = list(tqdm.tqdm(calc_pool.imap(pool_func, new_deals, chunksize=10), disable=True))
        calc_pool.close()
        calc_pool.join()
        for deal, (max_simul, max_coin, max_reserved, max_simul_same) in zip(
            new_deals, result
        ):
            deal[MAX_SIMULTANEOUS_DEALS_KEY] = max_simul
            deal[MAX_COIN_IN_DEALS_KEY] = max_coin
            deal[MAX_COIN_RESERVED_IN_DEALS_KEY] = max_reserved
            deal[MAX_SIMULTANEOUS_DEALS_SAME_BOT_KEY] = max_simul_same
    print("Total Elapsed Time: {:.3f}".format(time.time() - start_time))
    return new_deals


def _calculate_max_simultaneous_open_deals(current_deal, all_deals):
    """Returns the number of transactions that are overlapping.

    Note: all_deals should already be sorted by created_at date from newest to oldest
    """
    simultaneous_count = MaxValueTracker()
    coin_in_deals = MaxValueTracker()
    coin_reserved_in_deals = MaxValueTracker()
    simultaneous_same_bot_count = MaxValueTracker()
    overlap_deals = []
    for deal in all_deals:
        if deal["from_currency"] != current_deal["from_currency"]:
            continue
        now = datetime.utcnow()
        # # TODO: continue if current_deal start is after end of deal)
        # deal_end = gsheet_time_to_datetime(deal[DEAL_END_KEY]) if deal[DEAL_END_KEY] else now
        # if gsheet_time_to_datetime(current_deal[DEAL_START_KEY]) > deal_end:
        #     continue
        # # TODO: break if current_deal end is before start of deal
        # current_end = gsheet_time_to_datetime(current_deal[DEAL_END_KEY]) if current_deal[DEAL_END_KEY] else now
        # if current_end < gsheet_time_to_datetime(deal[DEAL_START_KEY]):
        #     break
        is_overlapping = _is_overlapping(
            deal[DEAL_START_KEY],
            deal[DEAL_END_KEY],
            current_deal[DEAL_START_KEY],
            current_deal[DEAL_END_KEY],
        )
        if is_overlapping:
            overlap_deals.append(deal)
            new_overlap_deals = []
            for overlap_deal in overlap_deals:
                if _is_overlapping(
                    deal[DEAL_START_KEY],
                    deal[DEAL_END_KEY],
                    overlap_deal[DEAL_START_KEY],
                    overlap_deal[DEAL_END_KEY],
                ):
                    new_overlap_deals.append(overlap_deal)
            overlap_deals = new_overlap_deals
            simultaneous_count.update_max_value(len(overlap_deals))
            for d in overlap_deals:
                # Failed to open deals have none for bought amount
                if d["bought_volume"]:
                    coin_in_deals.add_current_value(float(d["bought_volume"]))
                    coin_reserved_in_deals.add_current_value(
                        float(d["reserved_base_coin"])
                    )
                if deal["bot_id"] == d["bot_id"]:
                    simultaneous_same_bot_count.add_current_value(1)
            coin_in_deals.update_max_value(reset=True)
            coin_reserved_in_deals.update_max_value(reset=True)
            simultaneous_same_bot_count.update_max_value(reset=True)
    return (
        simultaneous_count.max_value,
        coin_in_deals.max_value,
        coin_reserved_in_deals.max_value,
        simultaneous_same_bot_count.max_value,
    )


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
    if start_2 >= start_1 and start_2 <= end_1:
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
    bot_info = BotInfo(cw)
    header = bot_info.bots[0].keys()
    with open(LOG_FILENAMES["BOTINFO"], "w") as bot_f:
        dict_writer = csv.DictWriter(bot_f, header)
        dict_writer.writeheader()
        dict_writer.writerows(bot_info.bots)


def print_bot_id_to_name_mapping(cw):
    bots = get_bots(cw)
    for bot in bots:
        print("{} -> {}".format(bot["id"], bot["name"]))


def get_name_from_id(cw, id):
    bots = get_bots(cw)
    for bot in bots:
        if bot["id"] == id:
            return bot["name"]
    raise Exception("No bot found with that id")


def write_log_with_deals(bot_id, deals):
    # TDOO: Need to deal with deals that were not completed but now are
    # Could rewrite whole file or find a way to replace just that row in file.
    log_filename = LOG_FILENAMES["DEAL_LOG"].format(bot_id)
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
    write_mode = "w"
    with open(log_filename, write_mode) as deal_log_f:
        dict_writer = csv.DictWriter(deal_log_f, header)
        if write_mode == "w":
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
