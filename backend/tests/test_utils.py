#!python3

###############################################################
# Imports
###############################################################


from waterer_backend.models import PUMP_UPDATE_TIME_FMT
from waterer_backend.utils import time_today_from_string, update_spans_activation_time

###############################################################
# Definitions
###############################################################

DETAILED_TIME_FMT = "%I:%M:%S %p"


###############################################################
# Tests
###############################################################


def test_activation_time_ctor_funcs():

    last_time_str = "7:59:45 AM"
    last_time = time_today_from_string(last_time_str, DETAILED_TIME_FMT)

    assert last_time.minute == 59
    assert last_time.second == 45


def test_update_span_func():

    last_time_str = "7:59:45 AM"
    last_time = time_today_from_string(last_time_str, DETAILED_TIME_FMT)

    update_time_str = "8:00 AM"

    curr_time_str = "8:01:12 AM"
    curr_time = time_today_from_string(curr_time_str, DETAILED_TIME_FMT)

    assert update_spans_activation_time(last_time, curr_time, update_time_str)


def test_update_on_update_pt_func():

    # on the boundary

    last_time_str = "7:59:45 AM"
    last_time = time_today_from_string(last_time_str, DETAILED_TIME_FMT)

    update_time_str = "8:00 AM"

    curr_time_str = "8:00:00 AM"
    curr_time = time_today_from_string(curr_time_str, DETAILED_TIME_FMT)

    assert update_spans_activation_time(last_time, curr_time, update_time_str)

    last_time = curr_time

    curr_time_str = "8:01:00 AM"
    curr_time = time_today_from_string(curr_time_str, DETAILED_TIME_FMT)

    assert not update_spans_activation_time(last_time, curr_time, update_time_str)

    # too late

    last_time = curr_time

    curr_time_str = "8:02:00 AM"
    curr_time = time_today_from_string(curr_time_str, DETAILED_TIME_FMT)

    assert not update_spans_activation_time(last_time, curr_time, update_time_str)

    # too early

    last_time_str = "7:02:00 AM"
    last_time = time_today_from_string(last_time_str, DETAILED_TIME_FMT)

    curr_time_str = "7:03:00 AM"
    curr_time = time_today_from_string(curr_time_str, DETAILED_TIME_FMT)

    assert not update_spans_activation_time(last_time, curr_time, update_time_str)
