# !python3

###############################################################
# Imports
###############################################################

import logging
import typing as ty
from dataclasses import asdict, dataclass
from threading import Event, Lock, Thread
from time import time

import numpy as np
from waterer_backend.embedded_arduino import EmbeddedArduino
from waterer_backend.request import Request
from waterer_backend.response import Response
from waterer_backend.status_log import BinaryStatusLog, FloatStatusLog

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)

###############################################################
# Class
###############################################################


@dataclass
class SmartPumpSettings:
    dry_humidity_V: float = 3.3
    wet_humidity_V: float = 0
    pump_on_time_s: int = 2
    pump_update_time_s: float = 600
    feedback_active: bool = False
    feedback_setpoint_pcnt: float = 50
    name: str = "Unamed pump"

    def __post_init__(self):
        self.validate()

    def validate(self):
        if self.wet_humidity_V > self.dry_humidity_V:
            raise ValueError(
                f"Wet humidity: {self.dry_humidity_V} V cannot exceed dry: {self.wet_humidity_V} V"
            )

        if self.pump_on_time_s < 0:
            raise ValueError(
                f"pump_on_time_s: {self.pump_on_time_s} s cannot be negative"
            )

        if self.pump_update_time_s < 0:
            raise ValueError(
                f"pump_on_time_s: {self.pump_update_time_s} s cannot be negative"
            )

        if self.pump_on_time_s > self.pump_update_time_s:
            raise ValueError(
                f"pump_on_time_s: {self.pump_on_time_s} s cannot exceed pump_update_time_s: {self.pump_update_time_s} s"
            )


@dataclass
class SmartPumpStatus:
    rel_humidity_V: float
    rel_humidity_pcnt: float
    pump_running: bool
    epoch_time: float


@dataclass
class SmartPumpStatusHistory:
    rel_humidity_V: ty.List[float]
    rel_humidity_V_epoch_time: ty.List[float]

    rel_humidity_pcnt: ty.List[float]
    rel_humidity_pcnt_epoch_time: ty.List[float]

    pump_running: ty.List[bool]
    pump_running_epoch_time: ty.List[float]


class SmartPump(Thread):
    def __init__(
        self,
        channel: int,
        device: ty.Optional[EmbeddedArduino],
        settings: SmartPumpSettings,
        status_update_interval_s: float = 5,
    ) -> None:

        Thread.__init__(self)

        self._device = device
        if device is None:
            _LOGGER.warning("Pump created without valid device")

        self._channel = channel

        self._settings_lock = Lock()

        with self._settings_lock:
            self._settings = settings

        self._sleep_event = Event()
        self._abort_running = False

        self._status_update_interval_s = status_update_interval_s

        self._rel_humidity_V_log = FloatStatusLog()
        self._rel_humidity_pcnt_log = FloatStatusLog()
        self._pump_status_log = BinaryStatusLog()

        self._last_feedback_update_time_s = time()

    @property
    def channel(self) -> int:
        return self._channel

    @property
    def settings(self) -> SmartPumpSettings:
        with self._settings_lock:
            return self._settings

    @settings.setter
    def settings(self, value: SmartPumpSettings) -> None:
        with self._settings_lock:
            self._settings = value
            _LOGGER.info(f"New setting for channel {self._channel}: {self._settings}")
            self._sleep_event.set()

    def _check_response(self, desc: str, response: Response) -> None:
        if not response.success:
            raise RuntimeError(f"Failed to {desc}: {response.message}")

    def _pcnt_from_V_humidity(self, rel_humidity_V: float) -> float:
        return (
            (self._settings.dry_humidity_V - rel_humidity_V)
            / (self._settings.dry_humidity_V - self._settings.wet_humidity_V)
            * 100
        )

    def turn_on(self):

        if self._device is None:
            _LOGGER.warning("No device connected")
            return

        response = self._device.make_request(
            Request(
                channel=self.channel,
                instruction="turn_on",
                data=0,
            )
        )
        self._check_response("turn_on", response)

    def turn_off(self):

        if self._device is None:
            _LOGGER.warning("No device connected")
            return

        response = self._device.make_request(
            Request(
                channel=self.channel,
                instruction="turn_off",
                data=0,
            )
        )
        self._check_response("turn_off", response)

    def _update_status(self) -> None:

        if self._device is None:
            _LOGGER.warning("No device connected")
            return

        _LOGGER.debug(f"Collecting status of pump: {self._channel}")

        response = self._device.make_request(
            Request(channel=self.channel, instruction="get_voltage", data=0)
        )
        self._check_response("get_humidity", response)

        rel_humidity_V = response.data
        rel_humidity_pcnt = self._pcnt_from_V_humidity(rel_humidity_V)

        response = self._device.make_request(
            Request(channel=self.channel, instruction="get_state", data=0)
        )
        self._check_response("get_pump_state", response)

        pump_status = bool(response.data)

        status_time = time()

        # log

        self._pump_status_log.add_sample(status_time, pump_status)
        self._rel_humidity_V_log.add_sample(status_time, rel_humidity_V)
        self._rel_humidity_pcnt_log.add_sample(status_time, rel_humidity_pcnt)

    @property
    def status(self) -> SmartPumpStatus:

        with self._settings_lock:

            self._update_status()

            status_time, pump_status = self._pump_status_log.get_newest_value()
            assert status_time is not None
            assert pump_status is not None

            _, rel_humidity_V = self._rel_humidity_V_log.get_newest_value()
            assert rel_humidity_V is not None

            _, rel_humidity_pcnt = self._rel_humidity_pcnt_log.get_newest_value()
            assert rel_humidity_pcnt is not None

            return SmartPumpStatus(
                rel_humidity_V, rel_humidity_pcnt, pump_status, status_time
            )

    def clear_status_logs(self):
        self._rel_humidity_pcnt_log.clear()
        self._rel_humidity_V_log.clear()
        self._pump_status_log.clear()

    def get_status_since(
        self, earliest_epoch_time_s: ty.Optional[float]
    ) -> SmartPumpStatusHistory:
        """
        if earliest time is None all samples are returned
        """
        rel_humidity_V_epoch_time, rel_humidity_V = self._rel_humidity_V_log.get_values(
            earliest_epoch_time_s
        )
        (
            rel_humidity_pcnt_epoch_time,
            rel_humidity_pcnt,
        ) = self._rel_humidity_pcnt_log.get_values(earliest_epoch_time_s)
        pump_running_epoch_time, pump_running = self._pump_status_log.get_values(
            earliest_epoch_time_s
        )

        return SmartPumpStatusHistory(
            rel_humidity_V=rel_humidity_V,
            rel_humidity_V_epoch_time=rel_humidity_V_epoch_time,
            rel_humidity_pcnt=rel_humidity_pcnt,
            rel_humidity_pcnt_epoch_time=rel_humidity_pcnt_epoch_time,
            pump_running_epoch_time=pump_running_epoch_time,
            pump_running=pump_running,
        )

    # Stops the feedback loop (so a join() should execute quickly)
    def interrupt(self):
        _LOGGER.info("Interrupting the pump thread")
        self._abort_running = True
        self._sleep_event.set()

    def run(self):

        if self._device is None:
            _LOGGER.warning("No device connected")
            return

        while not self._abort_running:

            self._sleep_event.clear()
            self._sleep_event.wait(timeout=self._status_update_interval_s)
            self._update_status()

            with self._settings_lock:
                wait_time_s = self._settings.pump_update_time_s
                if (
                    self._settings.feedback_active
                    and (time() - self._last_feedback_update_time_s) > wait_time_s
                ):
                    self._last_feedback_update_time_s = time()

                    response = self._device.make_request(
                        Request(
                            channel=self.channel,
                            instruction="get_voltage",
                            data=0,
                        )
                    )

                    if not response.success:
                        _LOGGER.warning(
                            f"Failed to get humidity for feedback: {response.message}"
                        )
                        continue

                    rel_humidity_pcnt = self._pcnt_from_V_humidity(response.data)

                    _LOGGER.info(
                        f"Measured relative humidity of {rel_humidity_pcnt} % (set point: {self._settings.feedback_setpoint_pcnt} %)"
                    )

                    if rel_humidity_pcnt < self._settings.feedback_setpoint_pcnt:
                        _LOGGER.info(
                            f"Activating pump for {self._settings.pump_on_time_s} s"
                        )

                        response = self._device.make_request(
                            Request(
                                channel=self.channel,
                                instruction="turn_on",
                                data=self._settings.pump_on_time_s,
                            )
                        )

                        if not response.success:
                            _LOGGER.warning(
                                f"Failed to activate pump: {response.message}"
                            )
                            continue

        _LOGGER.info(f"Smart pump for channel: {self._channel} finished")
