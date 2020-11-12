import functools

import py3cw  # type: ignore
from typing import Any, Dict, List

import request_helper


class AccountInfo:
    def __init__(self, cw: py3cw.Py3CW, real: bool = True) -> None:
        self.cw = cw
        mode: str
        if real:
            mode = 'real'
        else:
            mode = 'paper'
        success, accounts = self.cw.request(entity='users', action='change_mode', payload={'mode': mode})
        request_helper.check_if_request_successful(success)

    @property  # type: ignore
    @functools.lru_cache()
    def accounts(self) -> request_helper.Py3cw_request_info_list:
        success, accounts = self.cw.request(entity='accounts', action='')
        request_helper.check_if_request_successful(success)
        return accounts

    @functools.lru_cache()
    def account_table_data(self, account_id: int) -> request_helper.Py3cw_request_info:
        request_func = functools.partial(self.cw.request, entity='accounts', action='account_table_data', action_id=str(account_id))
        table_data = request_helper.check_with_retry(request_func)
        return table_data

    @property
    def account_ids(self) -> Dict[str, int]:
        account_ids = {}
        for account in self.accounts:
            account_ids[account['exchange_name']] = account['id']
        return account_ids

    def get_account_from_id(self, account_id: int) -> request_helper.Py3cw_request_info:
        for account in self.accounts:
            if account['id'] == account_id:
                return account
        raise Exception(f'No account with id: {account_id}')

    def get_account_balance(self, account_id: int) -> float:
        account = self.get_account_from_id(account_id)
        return float(account['btc_amount'])

    def get_account_profit(self, account_id: int) -> float:
        account = self.get_account_from_id(account_id)
        return float(account['day_profit_btc'])

    def get_coin_in_account(self, coin, account_id):
        request_func = functools.partial(self.cw.request, entity='accounts', action='pie_chart_data', action_id=str(account_id))
        pairs_info = request_helper.check_with_retry(request_func)
        for pair in pairs_info:
            if pair['code'] == coin:
                return pair['amount']

    def get_coin_reserved(self, coin, account_id):
        for coin_table_data in self.account_table_data(account_id):
            if coin_table_data['currency_code'] == coin.upper():
                return coin_table_data['on_orders']

    def get_coin_available(self, coin, account_id):
        for coin_table_data in self.account_table_data(account_id):
            if coin_table_data['currency_code'] == coin.upper():
                return coin_table_data['equity'] - coin_table_data['on_orders']
