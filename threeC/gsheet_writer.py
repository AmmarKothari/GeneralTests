import collections
from datetime import datetime

import pdb
import pygsheets

import account_info
import threeCDataGetter as tcdg

from constants import gsheet_date_only_format, GSHEET_UPDATE_LOG, gsheet_date_format


class GSheetWriter:
    def __init__(self, service_file, cw, output_gsheet):
        self.cw = cw

        self.gc = pygsheets.authorize(service_file=service_file)
        self.sh = self.gc.open(output_gsheet)

        self.account_info = account_info.AccountInfo(self.cw)

    def write_log_to_gsheet(self, bot_name, deals):
        if len(deals) == 0:
            print('No deals to write logs for')
            return

        # Gets all data into a list of lists
        data_matrix = [list(deals[0].keys())]
        for deal in deals:
            data_matrix.append(list(deal.values()))

        # Write to sheet
        wks = _get_worksheet_by_name(self.sh, bot_name)
        wks.clear(end='ZZ10000')
        if len(data_matrix) > wks.rows:
            print('Additional rows added')
            additional_rows = len(data_matrix) - wks.rows + 1
            wks.add_rows(additional_rows)
        wks.update_row(1, data_matrix)

    def write_bot_id_to_names_map_to_gsheet(self, bots, sheet_name):
        data_matrix = [['ID', 'Name']]
        for bot in bots:
            data_matrix.append([bot['id'], bot['name']])
        wks = _get_worksheet_by_name(self.sh, sheet_name)
        wks.update_row(1, data_matrix)

    def write_account_stats(self, sheet_name, account_key):
        # NOTE: Things will probably break if accounts are added
        records = collections.defaultdict(dict)
        wks = _get_worksheet_by_name(self.sh, sheet_name)
        all_rows = wks.get_all_values()
        for row in all_rows[1:]:
            if not row[0]:
                break
            records[row[0]]['Date'] = row[0]
            records[row[0]]['Value'] = row[1]
            records[row[0]]['Profit'] = row[2]

        date = datetime.utcnow().strftime(gsheet_date_only_format)
        account_id = self.account_info.account_ids[account_key]
        records[date]['Date'] = date
        records[date]['Value'] = self.account_info.get_account_balance(account_id)
        records[date]['Profit'] = self.account_info.get_account_profit(account_id)
        # Would be good to use a function to write these values to sheet from dictionary.  Could use some error checking.
        data_matrix = []
        headers = ['Date', 'Value', 'Profit']
        data_matrix.append(headers)
        for k, v in records.items():
            data_matrix.append(list(v.values()))

        wks.update_row(1, data_matrix)

    def update_last_write(self, elapsed_time=-1):
        wks = _get_worksheet_by_name(self.sh, GSHEET_UPDATE_LOG)
        wks.update_row(1, ['Last Update'])
        wks.insert_rows(1, number=1, values=[datetime.utcnow().strftime(gsheet_date_format), elapsed_time])


def _get_if_sheet_exists(sh, name):
    for wks in sh.worksheets():
        if wks.title == name:
            return wks
    return None


def _get_worksheet_by_name(sh, name):
    wks = _get_if_sheet_exists(sh, name)

    # Create sheet
    if not wks:
        wks = sh.add_worksheet(str(name))
    return wks


def read_worksheet(wks):
    # Read document into list of dicts where headers are keys
    keys = wks.get_row(1)
    i = 1
    input_data_matrix = []
    while True:
        i += 1
        row_vals = wks.get_row(i)
        if not row_vals:
            break
        row_dict = {}
        for k, v in zip(keys, row_vals):
            row_dict[k] = v
        input_data_matrix.append(row_dict)
    return input_data_matrix
