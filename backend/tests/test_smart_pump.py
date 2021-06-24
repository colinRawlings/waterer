#!python3

###############################################################
# Imports
###############################################################

from time import perf_counter, sleep

import matplotlib.pyplot as plt
import numpy as np
import waterer_backend.embedded_arduino as ae
from waterer_backend._test_utils import arduino_fxt
from waterer_backend.smart_pump import SmartPump, SmartPumpSettings

###############################################################
# Definitions
###############################################################

DEBUG = False  # display with matplotlib the results

###############################################################
# Tests
###############################################################


def test_turn_on_off_request(arduino_fxt: ae.EmbeddedArduino):

    smart_pump = SmartPump(2, arduino_fxt, SmartPumpSettings())

    results = smart_pump.status


def test_smart_pump(arduino_fxt: ae.EmbeddedArduino):

    time = []
    rel_humidity_pcnt = []
    pump_state = []

    if DEBUG:
        plt.ion()
        _, axs0 = plt.subplots()

        axs0.plot(time, rel_humidity_pcnt)
        axs0.set_xlabel("elapsed time [s]")
        axs0.set_ylabel("relative_humidity [%]")

        axs1 = axs0.twinx()

        axs1.plot(time, rel_humidity_pcnt)
        axs1.set_xlabel("elapsed time [s]")
        axs1.set_ylabel("relative_humidity [%]")

    smart_pump = SmartPump(
        2,
        arduino_fxt,
        SmartPumpSettings(
            pump_update_time_s=4,
            pump_on_time_s=2,
            feedback_active=True,
            feedback_setpoint_pcnt=100,  # feedback should activate
        ),
        status_update_interval_s=1,
    )
    smart_pump.start()

    pump_run_time_1_s = 10
    sleep(pump_run_time_1_s)

    status_history_1 = smart_pump.get_status_since(None)
    sampling_tolerance_s = 2

    assert (
        len(status_history_1.rel_humidity_V_epoch_time)
        >= pump_run_time_1_s - sampling_tolerance_s
    )
    assert (
        len(status_history_1.rel_humidity_V_epoch_time)
        < pump_run_time_1_s + sampling_tolerance_s
    )
    assert len(status_history_1.rel_humidity_V_epoch_time) == len(
        status_history_1.rel_humidity_V
    )

    assert any(status_history_1.pump_running)

    if DEBUG:
        axs0.plot(status_history_1.rel_humidity_V_epoch_time, status_history_1.rel_humidity_V, ".-b")  # type: ignore #matplotlib
        axs1.plot(status_history_1.pump_running_epoch_time, status_history_1.pump_running, ".-r")  # type: ignore #matplotlib
        plt.pause(0.001)  # type: ignore matplotlib

    # get recent log

    pump_run_time_2_s = 5
    sleep(pump_run_time_2_s)

    status_history_2 = smart_pump.get_status_since(
        status_history_1.rel_humidity_V_epoch_time[-1]
    )

    assert (
        len(status_history_2.rel_humidity_V_epoch_time)
        >= pump_run_time_2_s - sampling_tolerance_s
    )
    assert (
        len(status_history_2.rel_humidity_V_epoch_time)
        < pump_run_time_2_s + sampling_tolerance_s
    )

    assert all(
        np.array(status_history_2.rel_humidity_V_epoch_time)
        > status_history_1.rel_humidity_V_epoch_time[-1]
    )

    smart_pump.interrupt()
    smart_pump.join()

    if DEBUG:
        axs0.plot(status_history_2.rel_humidity_V_epoch_time, status_history_2.rel_humidity_V, "o-b")  # type: ignore #matplotlib
        axs1.plot(status_history_2.pump_running_epoch_time, status_history_2.pump_running, "o-r")  # type: ignore #matplotlib
        plt.show(block=True)  # type: ignore matplotlib
