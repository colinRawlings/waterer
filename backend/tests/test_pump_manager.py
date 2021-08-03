#!python3

###############################################################
# Imports
###############################################################

from time import perf_counter

import matplotlib.dates as mdate
import matplotlib.pyplot as plt
import waterer_backend.embedded_arduino as ae
import waterer_backend.pump_manager as pm
import waterer_backend.smart_pump as sp
from waterer_backend._test_utils import arduino_fxt, turn_on_request_fxt

###############################################################
# Definitions
###############################################################

DEBUG = False  # display with matplotlib the results

###############################################################
# Tests
###############################################################


def test_pump_manager():

    epoch_time = dict()
    rel_humidity_pcnts = dict()
    pump_states = dict()

    for channel in range(pm.NUM_PUMPS):
        epoch_time[channel] = list()
        rel_humidity_pcnts[channel] = list()
        pump_states[channel] = list()

    if DEBUG:
        plt.ion()
        fig, axs0 = plt.subplots(pm.NUM_PUMPS, 1)
        fig.autofmt_xdate()

        axs1 = list()
        for channel, ax0 in enumerate(axs0):  # type: ignore
            ax1 = ax0.twinx()

            ax0.set_xlabel("elapsed time [s]")
            ax0.set_ylabel("relative_humidity [%]")
            ax0.set_title(f"Channel: {channel}")

            ax1.set_xlabel("elapsed time [s]")
            ax1.set_ylabel("pump state")

            axs1.append(ax1)

            date_formatter = mdate.DateFormatter("%d-%m-%y %H:%M:%S")
            ax0.xaxis.set_major_formatter(date_formatter)
            ax1.xaxis.set_major_formatter(date_formatter)

        fig.tight_layout()

    with pm.PumpManagerContext(
        settings=sp.SmartPumpSettings(
            pump_activation_time="10:00 AM",
            pump_on_time_s=5,
            feedback_active=True,
            feedback_setpoint_pcnt=100,  # feedback should activate
        ),
        num_pumps=pm.NUM_PUMPS,
    ) as pump_manager:

        T0 = perf_counter()
        while perf_counter() - T0 < 30:

            for channel in range(pm.NUM_PUMPS):

                channel_status = pump_manager.get_status(channel)
                epoch_time[channel].append(channel_status.epoch_time)
                rel_humidity_pcnts[channel].append(channel_status.rel_humidity_pcnt)
                pump_states[channel].append(channel_status.pump_running)

                if DEBUG:
                    axs0[channel].plot(mdate.epoch2num(epoch_time[channel]), rel_humidity_pcnts[channel], ".-b")  # type: ignore
                    axs1[channel].plot(mdate.epoch2num(epoch_time[channel]), pump_states[channel], ".-r")  # type: ignore
                    plt.pause(0.001)  # type: ignore # matplotlib

    for channel in range(pm.NUM_PUMPS):
        assert any(pump_states[channel])
