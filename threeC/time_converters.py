from datetime import datetime

import constants


def gsheet_time_to_datetime(gsheet_time) -> datetime:
    return datetime.strptime(gsheet_time, constants.gsheet_date_format)


def threec_time_to_datetime(threec_time) -> datetime:
    try:
        return datetime.strptime(threec_time, constants.threeC_date_format)
    except ValueError as e:
        return datetime.strptime(threec_time, constants.threeC_date_format_no_T)
