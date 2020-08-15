import functools

from request_helper import _check_if_request_successful, _check_with_retry


class AccountInfo:
    def __init__(self, cw, real=True):
        self.cw = cw
        if real:
            mode = 'real'
        else:
            mode = 'paper'

        # import pdb; pdb.set_trace()
        # request_func = functools.partial(self.cw.request, entity='users', action='change_mode', payload={'mode': mode})
        # accounts = _check_with_retry(request_func)

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

    def get_btc_in_account(self, account_id):
        request_func = functools.partial(self.cw.request, entity='accounts', action='pie_chart_data', action_id=str(account_id))
        pairs_info = _check_with_retry(request_func)
        for pair in pairs_info:
            if pair['code'] == 'BTC':
                return pair['amount']
