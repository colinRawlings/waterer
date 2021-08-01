# !python3

###############################################################
# Imports
###############################################################

import logging
import traceback as tb
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
    num_smoothing_samples: float = 10
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

        if self.num_smoothing_samples <= 1:
            raise ValueError(
                f"Number of smoothing samples must be at least 1 (got: {self.num_smoothing_samples})"
            )


@dataclass
class SmartPumpStatus:
    rel_humidity_V: float
    rel_humidity_pcnt: float
    smoothed_rel_humidity_pcnt: ty.Optional[float]
    pump_running: int
    epoch_time: float


@dataclass
class SmartPumpStatusHistory:
    rel_humidity_V: ty.List[float]
    rel_humidity_V_epoch_time: ty.List[float]

    rel_humidity_pcnt: ty.List[float]
    rel_humidity_pcnt_epoch_time: ty.List[float]

    smoothed_rel_humidity_pcnt: ty.List[float]
    smoothed_rel_humidity_pcnt_epoch_time: ty.List[float]

    pump_running: ty.List[int]
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
        self._smoothed_rel_humidity_V_log = FloatStatusLog()
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

    def _pcnt_from_V_humidity(
        self, rel_humidity_V: ty.Union[None, float, ty.List[float]]
    ) -> ty.Union[None, float, ty.List[float]]:

        if rel_humidity_V is None:
            return None

        if isinstance(rel_humidity_V, list):

            arr = np.asarray(rel_humidity_V)
            none_vals = arr == None
            arr[none_vals] = 0

            scaled_arr = (
                (self._settings.dry_humidity_V - arr)
                / (self._settings.dry_humidity_V - self._settings.wet_humidity_V)
                * 100
            )

            scaled_optional_arr = scaled_arr
            scaled_optional_arr[none_vals] = None
            return scaled_optional_arr.tolist()

        else:
            return (
                (self._settings.dry_humidity_V - rel_humidity_V)
                / (self._settings.dry_humidity_V - self._settings.wet_humidity_V)
                * 100
            )

    def _smoothed_humidity(self, rel_humidity_V: float) -> ty.Optional[float]:
        alpha = 1.0 / self._settings.num_smoothing_samples
        _, last_value = self._smoothed_rel_humidity_V_log.get_newest_value()
        _, last_status = self._pump_status_log.get_newest_value()

        if last_status:
            # value not reliable while pump is running
            return None

        if last_value is None:
            return rel_humidity_V

        return alpha * rel_humidity_V + (1 - alpha) * last_value

    def turn_on(self, duration_s: int = 0):

        if self._device is None:
            _LOGGER.warning("No device connected")
            return

        response = self._device.make_request(
            Request(
                channel=self.channel,
                instruction="turn_on",
                data=duration_s,
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

    def _update_status(self) -> bool:

        if self._device is None:
            _LOGGER.warning("No device connected")
            return False

        _LOGGER.debug(f"Collecting status of pump: {self._channel}")

        ok, response = self._make_request_safe(
            Request(channel=self.channel, instruction="get_voltage", data=0)
        )
        if not ok:
            return False

        assert response is not None

        rel_humidity_V = response.data
        rel_humidity_pcnt = self._pcnt_from_V_humidity(rel_humidity_V)
        smoothed_rel_humidity_V = self._smoothed_humidity(rel_humidity_V)

        ok, response = self._make_request_safe(
            Request(channel=self.channel, instruction="get_state", data=0)
        )
        if not ok:
            return False

        assert response is not None

        pump_status = bool(response.data)
        status_time = time()

        # log

        self._pump_status_log.add_sample(status_time, pump_status)
        self._rel_humidity_V_log.add_sample(status_time, rel_humidity_V)
        self._smoothed_rel_humidity_V_log.add_sample(
            status_time, smoothed_rel_humidity_V
        )

        return True

    @property
    def status(self) -> SmartPumpStatus:

        with self._settings_lock:

            self._update_status()

            status_time, pump_status = self._pump_status_log.get_newest_value()
            assert status_time is not None
            assert pump_status is not None

            _, rel_humidity_V = self._rel_humidity_V_log.get_newest_value()
            assert rel_humidity_V is not None

            rel_humidity_pcnt = self._pcnt_from_V_humidity(rel_humidity_V)
            assert isinstance(rel_humidity_pcnt, float)

            (
                _,
                smoothed_rel_humidity_V,
            ) = self._smoothed_rel_humidity_V_log.get_newest_value()

            smoothed_rel_humidity_pcnt = self._pcnt_from_V_humidity(
                smoothed_rel_humidity_V
            )
            assert isinstance(smoothed_rel_humidity_pcnt, float)

            return SmartPumpStatus(
                rel_humidity_V,
                rel_humidity_pcnt,
                smoothed_rel_humidity_pcnt,
                pump_status,
                status_time,
            )

    def clear_status_logs(self):
        self._rel_humidity_V_log.clear()
        self._smoothed_rel_humidity_V_log.clear()
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

        rel_humidity_pcnt = self._pcnt_from_V_humidity(rel_humidity_V)
        assert isinstance(rel_humidity_pcnt, list)

        (
            smoothed_rel_humidity_V_epoch_time,
            smoothed_rel_humidity_V,
        ) = self._smoothed_rel_humidity_V_log.get_values(earliest_epoch_time_s)

        smoothed_rel_humidity_pcnt = self._pcnt_from_V_humidity(smoothed_rel_humidity_V)
        assert isinstance(smoothed_rel_humidity_pcnt, list)

        pump_running_epoch_time, pump_running = self._pump_status_log.get_values(
            earliest_epoch_time_s
        )

        return SmartPumpStatusHistory(
            rel_humidity_V=rel_humidity_V,
            rel_humidity_V_epoch_time=rel_humidity_V_epoch_time,
            rel_humidity_pcnt=rel_humidity_pcnt,
            rel_humidity_pcnt_epoch_time=rel_humidity_V_epoch_time,
            smoothed_rel_humidity_pcnt=smoothed_rel_humidity_pcnt,
            smoothed_rel_humidity_pcnt_epoch_time=smoothed_rel_humidity_V_epoch_time,
            pump_running_epoch_time=pump_running_epoch_time,
            pump_running=pump_running,
        )

    # Stops the feedback loop (so a join() should execute quickly)
    def interrupt(self):
        _LOGGER.info("Interrupting the pump thread")
        self._abort_running = True
        self._sleep_event.set()

    def _make_request_safe(
        self, request: Request
    ) -> ty.Tuple[bool, ty.Optional[Response]]:
        """Catch exceptions during request

        Args:
            request (Request): [description]

        Returns:
            bool: ok
        """

        task_desc = f"{request.instruction} on channel {self.channel}"

        assert self._device is not None

        try:
            response = self._device.make_request(request)
        except Exception as e:
            _LOGGER.error(
                f"Encountered exception {e} at {tb.format_exc()} \nwhile trying: {task_desc}"
            )
            return False, None

        if not response.success:
            _LOGGER.error(f"Failed to: {task_desc}")
            return False, None

        return True, response

    def run(self):

        if self._device is None:
            _LOGGER.warning("No device connected")
            return

        while not self._abort_running:

            self._sleep_event.clear()
            self._sleep_event.wait(timeout=self._status_update_interval_s)
            ok = self._update_status()
            if not ok:
                continue

            with self._settings_lock:
                wait_time_s = self._settings.pump_update_time_s
                if (
                    self._settings.feedback_active
                    and (time() - self._last_feedback_update_time_s) > wait_time_s
                ):

                    voltage_request = Request(
                        channel=self.channel,
                        instruction="get_voltage",
                        data=0,
                    )

                    ok, response = self._make_request_safe(voltage_request)
                    if not ok:
                        continue

                    assert response is not None

                    rel_humidity_pcnt = self._pcnt_from_V_humidity(response.data)
                    if rel_humidity_pcnt is None:
                        continue

                    assert isinstance(rel_humidity_pcnt, float)

                    _LOGGER.info(
                        f"Measured relative humidity of {rel_humidity_pcnt} % (set point: {self._settings.feedback_setpoint_pcnt} %)"
                    )

                    self._last_feedback_update_time_s = time()

                    if rel_humidity_pcnt < self._settings.feedback_setpoint_pcnt:
                        _LOGGER.info(
                            f"Activating pump for {self._settings.pump_on_time_s} s"
                        )

                    turn_on_request = Request(
                        channel=self.channel,
                        instruction="turn_on",
                        data=self._settings.pump_on_time_s,
                    )

                    ok, response = self._make_request_safe(turn_on_request)
                    if not ok:
                        continue

        _LOGGER.info(f"Smart pump for channel: {self._channel} finished")
