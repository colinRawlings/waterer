#!python3

###############################################################
# Imports
###############################################################

from time import perf_counter, sleep

import matplotlib.pyplot as plt
import waterer_backend.embedded_arduino as ae
from waterer_backend._test_utils import arduino_fxt, turn_on_request_fxt
from waterer_backend.smart_pump import SmartPump, SmartPumpSettings

###############################################################
# Definitions
###############################################################

DEBUG = True  # display with matplotlib the results

###############################################################
# Tests
###############################################################


def test_turn_on_off_request(arduino_fxt: ae.EmbeddedArduino):

    smart_pump = SmartPump(2, arduino_fxt, SmartPumpSettings())

    results = smart_pump.status


def test_threading(arduino_fxt: ae.EmbeddedArduino):

    time = []
    rel_humidity_pcnt = []
    pump_state = []

    if DEBUG:
        plt.ion()
        _, axs = plt.subplots(2, 1)

        axs[0].plot(time, rel_humidity_pcnt)
        axs[0].set_xlabel("elapsed time [s]")
        axs[0].set_ylabel("relative_humidity [%]")
        axs[0].plot(time, rel_humidity_pcnt, ".-b")

        axs[1].plot(time, rel_humidity_pcnt)
        axs[1].set_xlabel("elapsed time [s]")
        axs[1].set_ylabel("relative_humidity [%]")
        axs[1].plot(time, pump_state, ".-r")

    smart_pump = SmartPump(
        2,
        arduino_fxt,
        SmartPumpSettings(
            pump_update_time_s=2,
            pump_on_time_s=1,
            feedback_active=True,
            feedback_setpoint_pcnt=100,  # feedback should activate
        ),
    )
    smart_pump.start()

    T0 = perf_counter()
    while perf_counter() - T0 < 15:
        status = smart_pump.status

        time.append(perf_counter() - T0)
        rel_humidity_pcnt.append(status.rel_humidity_pcnt)
        pump_state.append(status.pump_running)

        if DEBUG:
            axs[0].plot(time, rel_humidity_pcnt, ".-b")
            axs[1].plot(time, pump_state, ".-r")
            plt.pause(0.001)

    smart_pump.interrupt()
    smart_pump.join()

    assert any(pump_state)