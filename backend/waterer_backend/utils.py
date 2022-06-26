#!python3

###############################################################
# Imports
###############################################################

import logging
from datetime import datetime, time

###############################################################
# Definitions
###############################################################

logger = logging.getLogger(__name__)

###############################################################
# Functions
###############################################################


def time_today_from_update_time(the_time: datetime) -> datetime:

    dt_today = datetime.now().date()

    return datetime.combine(dt_today, the_time.time())


###############################################################


def update_spans_activation_time(
    last_update_dt: datetime,
    current_dt: datetime,
    update_time: datetime,
    perform_hourly: bool,
) -> bool:

    if perform_hourly:

        current_hour = current_dt.hour
        last_update_hour = last_update_dt.hour

        result = current_hour > last_update_hour

        logger.debug(
            f"Feedback set to perform hourly: current_hour: {current_hour}, last_update_hour: {last_update_hour}, update_spans: {result}"
        )
        return result

    else:

        assert last_update_dt < current_dt

        update_dt_today = time_today_from_update_time(update_time)

        return last_update_dt < update_dt_today and update_dt_today <= current_dt


###############################################################


def day_of_the_year() -> int:
    return datetime.now().timetuple().tm_yday
