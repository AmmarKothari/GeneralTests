import copy
import csv
import datetime
import pickle
from collections import OrderedDict

import pdb
import pytest
import numpy as np

from threeC.threeCDataGetter import _calculate_all_max_simultaneous_open_deals
from threeC.constants import gsheet_date_format

RAW_BOT_LOGS_FN = "modified_bot_logs.p"


example_deal = OrderedDict(
    [
        ("id", "122616578"),
        ("type", "Deal"),
        ("bot_id", "1076305"),
        ("max_safety_orders", "2"),
        ("deal_has_error", "FALSE"),
        ("from_currency_id", "0"),
        ("to_currency_id", "0"),
        ("account_id", "29001794"),
        ("active_safety_orders_count", "1"),
        ("created_at", "05-29-2020 17:04:11"),
        ("updated_at", "05-29-2020 17:04:53"),
        ("closed_at", ""),
        ("finished?", "FALSE"),
        ("current_active_safety_orders_count", "1"),
        ("current_active_safety_orders", "1"),
        ("completed_safety_orders_count", "1"),
        ("completed_manual_safety_orders_count", "0"),
        ("cancellable?", "TRUE"),
        ("panic_sellable?", "TRUE"),
        ("trailing_enabled", "FALSE"),
        ("tsl_enabled", "FALSE"),
        ("stop_loss_timeout_enabled", "FALSE"),
        ("stop_loss_timeout_in_seconds", "0"),
        ("active_manual_safety_orders", "0"),
        ("pair", "BTC_LUN"),
        ("status", "bought"),
        ("take_profit", "0.8"),
        ("base_order_volume", "0.002"),
        ("safety_order_volume", "0.006"),
        ("safety_order_step_percentage", "0.4"),
        ("bought_amount", "88.73"),
        ("bought_volume", "0.008007212909"),
        ("bought_average_price", "0.00009024245361"),
        ("sold_amount", "0"),
        ("sold_volume", "0"),
        ("sold_average_price", "0"),
        ("take_profit_type", "total"),
        ("final_profit", "-0.00003836"),
        ("martingale_coefficient", "1"),
        ("martingale_volume_coefficient", "2"),
        ("martingale_step_coefficient", "2"),
        ("stop_loss_percentage", "0"),
        ("error_message", ""),
        ("profit_currency", "quote_currency"),
        ("stop_loss_type", "stop_loss"),
        ("safety_order_volume_type", "quote_currency"),
        ("base_order_volume_type", "quote_currency"),
        ("from_currency", "BTC"),
        ("to_currency", "LUN"),
        ("current_price", "8.97E-05"),
        ("take_profit_price", "0.0000911"),
        ("stop_loss_price", ""),
        ("final_profit_percentage", "0"),
        ("actual_profit_percentage", "-0.6"),
        ("bot_name", "Berlin (0.8%p, 10b, 3s, 3m) NEW"),
        ("account_name", ""),
        ("usd_final_profit", "-0.36"),
        ("actual_profit", "-0.00005609099"),
        ("actual_usd_profit", "-0.5286345834"),
        ("failed_message", ""),
        ("reserved_base_coin", "0.008007212909"),
        ("reserved_second_coin", "88.73"),
        ("trailing_deviation", "0.2"),
        ("trailing_max_price", ""),
        ("tsl_max_price", ""),
        ("strategy", "long"),
        ("duration", "76.61389"),
        ("max_simultaneous_deals", "1"),
        ("max_coin_in_deals", "0.008007212909"),
        ("max_coin_reserved_in_deals", "0.008007212909"),
        ("max_simultaneous_same_bot_deals", "1"),
        ("bot_group", "Berlin"),
    ]
)


def _deal_with_dates(start, end):
    deal = copy.deepcopy(example_deal)
    deal["created_at"] = start.strftime(gsheet_date_format)
    deal["closed_at"] = end.strftime(gsheet_date_format)
    return deal


@pytest.fixture
def empty_deals():
    return []


@pytest.fixture
def simple_sequential():
    # 1: |-------------------------------------------|
    # 2: |------|
    # 3:         |------|
    # 4:                  |------|
    # 5:                           |------|
    start = datetime.datetime.combine(
        datetime.date(2020, 1, 1), datetime.time(10, 0, 0, 0)
    )
    end = start + datetime.timedelta(hours=10)
    deals = [_deal_with_dates(start, end)]
    deal_start = start
    for i in range(4):
        end = deal_start + datetime.timedelta(hours=1)
        deals.append(_deal_with_dates(deal_start, end))
        deal_start = end + datetime.timedelta(seconds=1)
    return deals


@pytest.fixture
def overlapping_set():
    # 1: |-------------------------------------------|
    # 2: |------|
    # 3: |------|
    # 4: |------|
    # 5: |------|
    start = datetime.datetime.combine(
        datetime.date(2020, 1, 1), datetime.time(10, 0, 0, 0)
    )
    end = start + datetime.timedelta(hours=10)
    deals = [_deal_with_dates(start, end)]
    deal_start = start
    end = deal_start + datetime.timedelta(hours=1)
    deal = _deal_with_dates(deal_start, end)
    for i in range(4):
        deals.append(deal)
    return deals


@pytest.fixture
def overlapping_with_random_end_set():
    # 1: |-------------------------------------------|
    # (example below will be more random)
    # 2: |------|
    # 3: |------------------|
    # 4: |----------|
    # 5: |--------------------------|
    start = datetime.datetime.combine(
        datetime.date(2020, 1, 1), datetime.time(10, 0, 0, 0)
    )
    end = start + datetime.timedelta(hours=10)
    deals = [_deal_with_dates(start, end)]
    for i in range(4):
        end = start + datetime.timedelta(hours=np.random.randint(1, 9))
        deals.append(_deal_with_dates(start, end))
    return deals


@pytest.fixture
def raw_bot_logs():
    logs = pickle.load(open(RAW_BOT_LOGS_FN), "rb")
    return logs


def test_empty_deals(empty_deals):
    deals = _calculate_all_max_simultaneous_open_deals(empty_deals)
    assert len(deals) == 0


def test_sequential_set(simple_sequential):
    deals = _calculate_all_max_simultaneous_open_deals(simple_sequential)
    assert all([d["max_simultaneous_deals"] == 2 for d in deals])


def test_overlapping_set(overlapping_set):
    deals = _calculate_all_max_simultaneous_open_deals(overlapping_set)
    assert all([d["max_simultaneous_deals"] == 5 for d in deals])


def test_overlapping_with_random_end_set(overlapping_with_random_end_set):
    deals = _calculate_all_max_simultaneous_open_deals(overlapping_with_random_end_set)
    assert all([d["max_simultaneous_deals"] == 5 for d in deals])
