from datetime import datetime

from constants import gsheet_date_format


def gsheet_time_to_datetime(gsheet_time):
    return datetime.strptime(gsheet_time, gsheet_date_format)
