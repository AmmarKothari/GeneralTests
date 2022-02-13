import collections
from datetime import datetime
from typing import List, Any, Dict

import googleapiclient.errors  # type: ignore
import pygsheets  # type:ignore
import pygsheets.client  # type:ignore

from constants import gsheet_date_only_format, GSHEET_UPDATE_LOG, gsheet_date_format


MAX_RETRIES = 5

HEADER = ['Date', 'Value', 'Profit',
          'BTC', 'BTC_Available', 'BTC_Reserved',
          'BNB', 'BNB_Available', 'BNB_Reserved',
          'ETH', 'ETH_Available', 'ETH_Reserved',
          'USDT', 'USDT_Available', 'USDT_Reserved',
          'USD', 'USD_Available', 'USD_Reserved'
          ]

class GSheetWriter:
    def __init__(self, service_file: str, output_gsheet: str):
        self.gc: pygsheets.client.Client = pygsheets.authorize(
            service_file=service_file
        )
        retry_counter: int = 0
        while retry_counter <= MAX_RETRIES:
            try:
                self.sh: pygsheets.spreadsheet.Spreadsheet = self.gc.open(output_gsheet)
                break
            except googleapiclient.errors.HttpError:
                retry_counter += 1
                print(f"Failed to connect to GSheets.  Retry attempt: {retry_counter}")
                if retry_counter > MAX_RETRIES:
                    raise

    # TODO: Add method that can change from datetime to gsheet time string for an entire column

    def write_log_to_gsheet(self, sheet_name: str, deals: List[Dict[str, Any]], start_row: int = 0, include_header: bool = False) -> None:
        if len(deals) == 0:
            print("No deals to write logs for")
            return

        # Gets all data into a list of lists
        data_matrix = []
        if include_header:
            data_matrix.append(list(deals[0].keys()))
        for deal in deals:
            data_matrix.append(list(deal.values()))

        # Write to sheet
        wks = _get_worksheet_by_name(self.sh, sheet_name)
        wks.clear(start=f"A{start_row}", end=f"ZZ{start_row+10000}")
        if len(data_matrix) > (wks.rows - start_row):
            print("Additional rows added")
            additional_rows = len(data_matrix) - (wks.rows - start_row) + 1
            wks.add_rows(additional_rows)
        wks.update_row(start_row, data_matrix)

    def write_bot_id_to_names_map_to_gsheet(
        self, bots: List[Dict[str, Any]], sheet_name: str
    ) -> None:
        data_matrix = [["ID", "Name"]]
        for bot in bots:
            data_matrix.append([bot["id"], bot["name"]])
        wks = _get_worksheet_by_name(self.sh, sheet_name)
        wks.update_row(1, data_matrix)

    def combine_account_stats(self, account_infos: List[Dict[str, Any]]) -> Dict[str, Any]:
        accumulated_stats = collections.defaultdict(float)
        for account_info_with_date_key in account_infos:
            # Should only be one item in list.  Pop it and get the values.
            account_info = account_info_with_date_key.popitem()[1]
            for h in HEADER:
                if h == "Date":
                    accumulated_stats[h] = account_info[h]
                else:
                    # Everything else is a float that can be summed
                    if h in account_info.keys():
                        accumulated_stats[h] += account_info[h]
                    else:
                        accumulated_stats[h] += 0.0
        # Because of a poor formatting choice for account stats, add the date key in. FIX!
        formatted_accumualted_stats = {}
        formatted_accumualted_stats[accumulated_stats["Date"]] = accumulated_stats
        return formatted_accumualted_stats


    def write_account_stats(self, sheet_name: str, account_info: Dict[str, Any]) -> None:
        # TODO: Don't read and write the whole thing every time.  Just add a row at the bottom and add values there. Unclear if headers should be updated?
        # NOTE: Things will probably break if accounts are added
        records = collections.defaultdict(dict)
        wks = _get_worksheet_by_name(self.sh, sheet_name)
        all_rows = wks.get_all_values()
        # Get the header of the sheet.
        # If different, log message and update header.
        # This is probably a pretty general function.
        for row in all_rows[1:]:
            if not row[0]:
                break
            for i, h in enumerate(HEADER):
                try:
                    records[row[0]][h] = row[i]
                except IndexError:
                    # The value didn't exist for that row so just fill in with 0.0 for now?
                    records[row[0]][h] = 0.0

        records.update(account_info)
        # Would be good to use a function to write these values to sheet from dictionary.  Could use some error checking.
        data_matrix = []
        data_matrix.append(HEADER)
        for k, v in records.items():
            data_matrix.append(list(v.values()))
        wks.update_row(1, data_matrix)

    def update_last_write(self, elapsed_time=-1):
        wks = _get_worksheet_by_name(self.sh, GSHEET_UPDATE_LOG)
        wks.update_row(1, ["Last Update"])
        wks.insert_rows(
            1,
            number=1,
            values=[datetime.utcnow().strftime(gsheet_date_format), elapsed_time],
        )


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
