# !python3

###############################################################
# Imports
###############################################################

import asyncio
import json
import logging
import os
import struct
import traceback as tb
import typing as ty
from datetime import datetime
from time import time

import bleak
import numpy as np
from bleak.backends.device import BLEDevice
from waterer_backend.BLE.BLE_ids import (
    HUMIDITY_ATTR_ID,
    PUMP_ATTR_ID,
    PUMP_STATUS_ATTR_ID,
)
from waterer_backend.config import get_history_filepath
from waterer_backend.models import (
    SmartPumpSettings,
    SmartPumpStatus,
    SmartPumpStatusData,
    SmartPumpStatusHistory,
)
from waterer_backend.status_log import BinaryStatusLog, FloatStatusLog
from waterer_backend.utils import update_spans_activation_time

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)


###############################################################
# Classes
###############################################################


class BLESmartPump:
    def __init__(
        self,
        channel: int,
        client: ty.Optional[bleak.BleakClient],
        pump_device: ty.Optional[BLEDevice],
        settings: SmartPumpSettings,
        status_update_interval_s: float = 5,
        allow_load_history: bool = False,
        auto_save_interval_s: ty.Optional[int] = 3600,
    ) -> None:

        self._client = client
        if client is None:
            _LOGGER.warning("Pump created without valid client")

        self._pump_device = pump_device
        if client is None:
            _LOGGER.warning("Pump created without valid device")

        self._task: ty.Optional[asyncio.Task] = None

        self._channel = channel

        self._settings = settings

        self._abort_running = False

        self._status_update_interval_s = status_update_interval_s
        self._auto_save_interval_s = auto_save_interval_s

        if allow_load_history:
            self.load_history()
        else:
            self._init_logs()

        self._last_feedback_update_time: ty.Optional[datetime] = None
        self._last_auto_save_time: float = time()

    def _init_logs(self):
        self._rel_humidity_V_log = FloatStatusLog()
        self._smoothed_rel_humidity_V_log = FloatStatusLog()
        self._pump_status_log = BinaryStatusLog()

    @property
    def info(self) -> str:
        assert self._client is not None
        assert self._pump_device is not None
        return f"{self._client.address}, signal strength: {self._pump_device.rssi} dBm"

    @property
    def channel(self) -> int:
        return self._channel

    @property
    def settings(self) -> SmartPumpSettings:
        return self._settings

    @settings.setter
    def settings(self, value: SmartPumpSettings) -> None:
        self._settings = value
        _LOGGER.info(f"{self._channel}: New settings: {self._settings}")

    def save_history(self) -> None:

        history = SmartPumpStatusData(
            rel_humidity_V_log=self._rel_humidity_V_log.to_data(),
            smoothed_rel_humidity_V_log=self._smoothed_rel_humidity_V_log.to_data(),
            pump_status_log=self._pump_status_log.to_data(),
        )

        filepath = get_history_filepath(self._channel)

        os.makedirs(filepath.parent, exist_ok=True)

        with open(filepath, "w") as fh:
            json.dump(history.dict(), fh)

        _LOGGER.info(f"{self._channel}: Saved history to {filepath}")

    def load_history(self) -> None:
        filepath = get_history_filepath(self._channel)

        if not filepath.is_file():
            _LOGGER.info(
                f"{self._channel}: Failed to find history file for: {filepath}"
            )
            self._init_logs()
            return

        with open(filepath, "r") as fh:
            history_dict = json.load(fh)

        try:
            history = SmartPumpStatusData(**history_dict)
        except Exception as e:
            _LOGGER.error(
                f"{self._channel}: Failed to parse history file: {filepath} with exception{e}"
            )
            self._init_logs()
            return

        _LOGGER.info(f"{self._channel}: Loaded history from {filepath}")

        self._rel_humidity_V_log = FloatStatusLog.from_data(history.rel_humidity_V_log)
        self._smoothed_rel_humidity_V_log = FloatStatusLog.from_data(
            history.smoothed_rel_humidity_V_log
        )
        self._pump_status_log = BinaryStatusLog.from_data(history.pump_status_log)

    def _pcnt_from_V_humidity(
        self, rel_humidity_V: ty.Union[None, float, ty.List[ty.Optional[float]]]
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

    async def check_client(self) -> bool:

        if self._client is None:
            _LOGGER.warning("No device connected")
            return False

        return self._client.is_connected  # n.b. log warning on disconnect

    async def turn_on(self, duration_ms: int = -1):

        if not await self.check_client():
            _LOGGER.info("{self.channel}: turn_on: failed check_client")
            return

        assert self._client is not None

        on_code_bytes = bytearray(struct.pack("<I", duration_ms))

        current_char_bytes = await self._client.read_gatt_char(PUMP_ATTR_ID)
        _LOGGER.info(
            f"{self.channel}: preparing to write {on_code_bytes} (current: {current_char_bytes})"
        )

        await self._client.write_gatt_char(PUMP_ATTR_ID, on_code_bytes)

    async def turn_off(self):

        if not await self.check_client():
            _LOGGER.info("{self.channel}: turn_off: failed check_client")
            return

        assert self._client is not None

        off_code_bytes = struct.pack("<I", 0)

        current_char_bytes = await self._client.read_gatt_char(PUMP_ATTR_ID)
        _LOGGER.debug(
            f"{self.channel}: preparing to write {off_code_bytes} (current: {current_char_bytes})"
        )

        await self._client.write_gatt_char(PUMP_ATTR_ID, off_code_bytes)

    ###############################################################
    # Access Data
    ###############################################################

    async def get_humidity_V(self) -> float:

        if not await self.check_client():
            _LOGGER.info(
                "{self.channel}: get_humidity_V: no client returning a humidity of 0.5 V"
            )
            return 0.5

        assert self._client is not None

        humidity_bytes = await self._client.read_gatt_char(HUMIDITY_ATTR_ID)
        return struct.unpack("f", humidity_bytes)[0]

    async def get_pump_status(self) -> bool:
        if not await self.check_client():
            _LOGGER.info(
                "{self.channel}: get_pump_status: no client returning a pump status of False"
            )
            return False

        assert self._client is not None

        status_bytes = await self._client.read_gatt_char(PUMP_STATUS_ATTR_ID)
        return struct.unpack("b", status_bytes)[0]  # type: ignore

    async def _update_status(self) -> bool:

        if self._client is None:
            _LOGGER.warning("No device connected")
            return False

        _LOGGER.debug(f"Collecting status of pump: {self._channel}")

        rel_humidity_V = await self.get_humidity_V()
        rel_humidity_pcnt = self._pcnt_from_V_humidity(rel_humidity_V)
        smoothed_rel_humidity_V = self._smoothed_humidity(rel_humidity_V)

        pump_status = await self.get_pump_status()
        status_time = time()

        # log

        self._pump_status_log.add_sample(status_time, pump_status)
        self._rel_humidity_V_log.add_sample(status_time, rel_humidity_V)
        self._smoothed_rel_humidity_V_log.add_sample(
            status_time, smoothed_rel_humidity_V
        )

        # save

        if self._auto_save_interval_s is not None and (
            (time() - self._last_auto_save_time) > self._auto_save_interval_s
        ):
            self.save_history()
            self._last_auto_save_time = time()

        return True

    @property
    async def status(self) -> SmartPumpStatus:

        await self._update_status()

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

        smoothed_rel_humidity_pcnt = self._pcnt_from_V_humidity(smoothed_rel_humidity_V)
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

    async def _do_activate_closed_loop_pump(self):

        (
            _,
            current_humidity_V,
        ) = self._smoothed_rel_humidity_V_log.get_newest_value()
        current_humidity_pcnt = self._pcnt_from_V_humidity(current_humidity_V)

        _LOGGER.info(
            f"{self.channel}: Humidity: Current: {current_humidity_pcnt} %, Target: {self._settings.feedback_setpoint_pcnt} %"
        )

        if (
            isinstance(current_humidity_pcnt, float)
            and self._settings.feedback_setpoint_pcnt > current_humidity_pcnt
        ):
            _LOGGER.info(
                f"{self.channel}: Activating pump for {self._settings.pump_on_time_s} s"
            )

            await self.turn_on(self._settings.pump_on_time_s)

    async def _do_loop_iteration(self):

        ok = await self._update_status()
        if not ok:
            return

        next_update_time = datetime.now()

        should_activate = (
            self._last_feedback_update_time is not None
            and update_spans_activation_time(
                self._last_feedback_update_time,
                next_update_time,
                self._settings.pump_activation_time,
            )
        )

        self._last_feedback_update_time = next_update_time

        if should_activate:
            _LOGGER.info(f"{self.channel}: Performing feedback event: ")
            await self._do_activate_closed_loop_pump()

    async def run(self):

        while not self._abort_running:
            try:
                await self._do_loop_iteration()
                await asyncio.sleep(self._status_update_interval_s)
            except asyncio.CancelledError:
                _LOGGER.info(f"{self._channel}: run cancelled, stopping ...")
                break
            except Exception as e:
                _LOGGER.error(
                    f"{self.channel}: Encountered exception in run loop:\n\n{tb.format_exc()}"
                )

        _LOGGER.info(f"{self.channel}: run() finished")

    def start(self):
        self._task = asyncio.get_event_loop().create_task(
            self.run(), name=f"main_loop_pump_{self.channel}"
        )

    # Stops the feedback loop
    async def interrupt(self):

        if self._task is not None and not self._task.done():
            self._task.cancel()
            await self._task
