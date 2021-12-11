import collections
import functools
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, OrderedDict, Union, cast

from py3cw import request as py3cw_req  # type: ignore

import constants
import request_helper


class AccountException(Exception):
    pass


class AccountInfo:
    def __init__(self, cw: py3cw_req.Py3CW, real: bool = True) -> None:
        self.cw = cw
        if real:
            mode = "real"
        else:
            mode = "paper"
        success, accounts = self.cw.request(
            entity="users", action="change_mode", payload={"mode": mode}
        )
        request_helper.check_if_request_successful(success)
        self._accounts: Optional[request_helper.Py3cw_request_info_list] = None
        self._account_index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._account_index < len(self.accounts):
            self._account_index += 1
            return self._accounts[self._account_index - 1]

        raise StopIteration

    @functools.lru_cache()
    def account_table_data(
        self, account_id: int
    ) -> request_helper.Py3cw_request_info_list:
        request_func: Callable[
            [], request_helper.Py3cw_request_list_response
        ] = functools.partial(
            self.cw.request,
            entity="accounts",
            action="account_table_data",
            action_id=str(account_id),
        )
        table_data = request_helper.check_with_retry(request_func)
        table_data = cast(request_helper.Py3cw_request_info_list, table_data)
        return table_data

    @property  # type: ignore
    def accounts(self) -> request_helper.Py3cw_request_info_list:
        if self._accounts:
            return self._accounts
        request_func: Callable[
            [], request_helper.Py3cw_request_list_response
        ] = functools.partial(self.cw.request, entity="accounts", action="")
        accounts = request_helper.check_with_retry(request_func)
        accounts = cast(request_helper.Py3cw_request_info_list, accounts)
        self._accounts = accounts
        return accounts

    @property
    def account_ids(self) -> Dict[str, int]:
        account_ids: Dict[str, int] = {}
        for account in self.accounts:
            if account:
                account_ids[account["name"]] = cast(int, account["id"])
        return account_ids

    def get_account_from_id(
        self, account_id: int
    ) -> request_helper.Py3cw_request_info_single_success:
        for account in self.accounts:
            if account:
                if account["id"] == account_id:
                    return account
        raise AccountException(f"No account with id: {account_id}")

    def get_account_from_name(self, account_name: str) -> request_helper.Py3cw_request_info_single_success:
        for account in self.accounts:
            if account['name'] == account_name:
                return account
        raise AccountException(f"No account width name: {account_name}")

    def get_account_balance(self, account_id: int) -> float:
        account = self.get_account_from_id(account_id)
        return float(account["btc_amount"])

    def get_account_profit(self, account_id: int) -> float:
        account = self.get_account_from_id(account_id)
        return float(account["day_profit_btc"])

    @functools.lru_cache()
    def get_coin_in_account(self, coin: str, account_id: int) -> float:
        request_func: Callable[
            [], request_helper.Py3cw_request_list_response
        ] = functools.partial(
            self.cw.request,
            entity="accounts",
            action="pie_chart_data",
            action_id=str(account_id),
        )
        pairs_info = request_helper.check_with_retry(request_func)
        pairs_info = cast(List[Dict[str, Any]], pairs_info)
        for pair in pairs_info:
            if pair["code"] == coin:
                return cast(float, pair["amount"])
        raise AccountException(
            f"Coin {coin} not in account {account_id}.  Could be invalid coin or account id."
        )

    def get_coin_reserved(self, coin: str, account_id: int) -> float:
        for coin_table_data in self.account_table_data(account_id):
            if coin_table_data["currency_code"] == coin.upper():
                return coin_table_data["on_orders"]
        raise Exception(
            f"Coin {coin} not in account {account_id}.  Could be invalid coin or account id."
        )

    def get_coin_available(self, coin: str, account_id: int) -> float:
        for coin_table_data in self.account_table_data(account_id):
            if coin_table_data["currency_code"] == coin.upper():
                return coin_table_data["equity"] - coin_table_data["on_orders"]
        raise AccountException(
            f"Coin {coin} not in account {account_id}.  Could be invalid coin or account id."
        )

    def get_account_stats(
        self, account_name: str
    ) -> Dict[str, "OrderedDict[str, Union[str, float]]"]:
        # NOTE: Things will probably break if accounts are added
        date: str = datetime.utcnow().strftime(constants.gsheet_date_only_format)
        account_id = self.account_ids[account_name]

        # TODO: Remove the date as a key.  WHY?!?!
        records: Dict[
            str, collections.OrderedDict[str, Union[str, float]]
        ] = collections.defaultdict(collections.OrderedDict)
        records[date]["Date"] = date
        records[date]["Value"] = self.get_account_balance(account_id)
        records[date]["Profit"] = self.get_account_profit(account_id)

        coins_of_interest = ["BTC", "BNB", "ETH", "USDT"]
        for coin in coins_of_interest:
            try:
                records[date][coin] = self.get_coin_in_account(coin, account_id)
                records[date][f"{coin}_Available"] = self.get_coin_available(
                    coin, account_id
                )
                records[date][f"{coin}_Reserved"] = self.get_coin_reserved(
                    coin, account_id
                )
            except AccountException as e:
                print(e)
        return records
