# !python3

###############################################################
# Imports
###############################################################

import logging
from dataclasses import dataclass
from threading import Event, Lock, Thread
from time import sleep

from waterer_backend.embedded_arduino import EmbeddedArduino
from waterer_backend.request import Request
from waterer_backend.response import Response

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)

###############################################################
# Class
###############################################################


@dataclass
class SmartPumpSettings:
    dry_humidity_V: float = 0
    wet_humidity_V: float = 3.3
    pump_on_time_s: int = 2
    pump_update_time_s: float = 600
    feedback_active: bool = False
    feedback_setpoint_pcnt: float = 50

    def __post_init__(self):
        if self.wet_humidity_V < self.dry_humidity_V:
            raise ValueError(
                f"Dry humidity: {self.dry_humidity_V} V cannot exceed wet: {self.wet_humidity_V} V"
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


class SmartPump(Thread):
    def __init__(
        self, channel: int, device: EmbeddedArduino, settings: SmartPumpSettings
    ) -> None:

        Thread.__init__(self)

        self._device = device
        self._channel = channel

        self._settings_lock = Lock()

        with self._settings_lock:
            self._settings = settings

        self._sleep_event = Event()
        self._abort_running = False

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
            self._sleep_event.set()

    def _check_response(self, desc: str, response: Response) -> None:
        if not response.success:
            raise RuntimeError(f"Failed to {desc}: {response.message}")

    def _pcnt_from_V_humidity(self, rel_humidity_V: float) -> float:
        return (
            (rel_humidity_V - self._settings.dry_humidity_V)
            / (self._settings.wet_humidity_V - self._settings.dry_humidity_V)
            * 100
        )

    # TODO value qualification ...
    def set_dry(self, dry_V: float) -> None:
        with self._settings_lock:
            self._settings.dry_humidity_V = dry_V

    def set_wet(self, wet_V: float) -> None:
        with self._settings_lock:
            self._settings.wet_humidity_V = wet_V

    def calibrate_dry(self) -> None:

        with self._settings_lock:

            response = self._device.make_request(
                Request(channel=self.channel, instruction="get_voltage", data=0)
            )
            self._check_response("calibrate_dry", response)

            self._settings.dry_humidity_V = response.data

    def calibrate_wet(self) -> None:

        with self._settings_lock:

            response = self._device.make_request(
                Request(channel=self.channel, instruction="get_voltage", data=0)
            )

            self._check_response("calibrate_wet", response)

            self._settings.wet_humidity_V = response.data

    @property
    def status(self) -> SmartPumpStatus:

        with self._settings_lock:
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

            return SmartPumpStatus(
                rel_humidity_V, rel_humidity_pcnt, bool(response.data)
            )

    # Stops the feedback loop (so a join() should execute quickly)
    def interrupt(self):
        _LOGGER.info("Interrupting the pump thread")
        self._sleep_event.set()
        self._abort_running = True

    def run(self):

        while not self._abort_running:

            with self._settings_lock:
                wait_time_s = self._settings.pump_update_time_s

            self._sleep_event.clear()
            self._sleep_event.wait(timeout=wait_time_s)

            with self._settings_lock:
                if self._settings.feedback_active:

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
