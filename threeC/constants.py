# CSV name to hold account value log
CSV_ACCOUNT_VALUE_LOG = "Raw_AccountValue.csv"

threeC_date_format = '%Y-%m-%dT%H:%M:%S.%fZ'
gsheet_date_format = '%m-%d-%Y %H:%M:%S.%f'
gsheet_date_only_format = '%m-%d-%Y'


MAIN_ACCOUNT_KEY = 'Exchange Wallet'

GSHEET_UPDATE_LOG = 'Raw_UpdateLog'

LAST_RUN_SUCCESS_CACHE = 'cache_files/last_run_successful.cache'
DEAL_START_KEY = 'created_at'
DEAL_UPDATED_KEY = 'updated_at'
DEAL_END_KEY = 'closed_at'
CONVERT_TO_DATE_TIME = [DEAL_START_KEY, DEAL_UPDATED_KEY, DEAL_END_KEY]