#!python3

###############################################################
# Imports
###############################################################

from datetime import datetime, time

###############################################################
# Functions
###############################################################


def time_today_from_update_time(the_time: datetime) -> datetime:

    dt_today = datetime.now().date()

    return datetime.combine(dt_today, the_time.time())


###############################################################


def update_spans_activation_time(
    last_update_dt: datetime, current_dt: datetime, update_time: datetime
) -> bool:

    assert last_update_dt < current_dt

    update_dt_today = time_today_from_update_time(update_time)

    return last_update_dt < update_dt_today and update_dt_today <= current_dt
