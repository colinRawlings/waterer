#!python3

###############################################################
# Imports
###############################################################

from datetime import datetime, time

from waterer_backend.models import PUMP_UPDATE_TIME_FMT

###############################################################
# Functions
###############################################################


def time_from_string(time_str: str, fmt: str = PUMP_UPDATE_TIME_FMT) -> time:

    dt = datetime.strptime(time_str, fmt)

    return dt.time()


###############################################################


def time_today_from_string(time_str: str, fmt: str = PUMP_UPDATE_TIME_FMT) -> datetime:

    tm = time_from_string(time_str, fmt)

    dt_today = datetime.now().date()

    return datetime.combine(dt_today, tm)


###############################################################


def update_spans_activation_time(
    last_update_dt: datetime, current_dt: datetime, update_time_str: str
) -> bool:

    assert last_update_dt < current_dt

    update_dt_today = time_today_from_string(update_time_str)

    return last_update_dt < update_dt_today and update_dt_today <= current_dt
