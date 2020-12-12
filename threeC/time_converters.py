from datetime import datetime

import constants


def gsheet_time_to_datetime(gsheet_time) -> datetime:
    return datetime.strptime(gsheet_time, constants.gsheet_date_format)


def threec_time_to_datetime(gsheet_time) -> datetime:
    return datetime.strptime(gsheet_time, constants.threeC_date_format)
