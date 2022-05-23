#!python3

###############################################################
# Import
###############################################################
import logging
import pathlib as pt
from typing import List, Optional, Union

import numpy as np
import waterer_backend.smart_pump as sp
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from waterer_backend.BLE.BLE_ids import PUMP_NAME
from waterer_backend.BLE.BLEsmart_pump import BLESmartPump
from waterer_backend.config import get_history_dir, save_user_pumps_config

###############################################################
# Definitions
###############################################################

logger = logging.getLogger(__name__)

SCAN_DURATION_S = 5

MIN_RSSI = -95

###############################################################
# Class
###############################################################

pump_manager_settings_type = Union[List[sp.SmartPumpSettings], sp.SmartPumpSettings]


class BLEPumpManager:
    def __init__(
        self,
        settings: pump_manager_settings_type,
        status_update_interval_s: int = 5,
        clients: List[BleakClient] = [],
        pump_devices: List[BLEDevice] = [],
        config_filepath: Optional[pt.Path] = None,
        allow_load_history: bool = True,
    ) -> None:

        self._status_update_interval_s = status_update_interval_s
        self._clients = clients

        if isinstance(settings, sp.SmartPumpSettings):

            logger.info(f"Duplicating supplied settings for {len(clients)} client(s)")
            self._init_settings = [settings for _ in range(len(clients))]
        elif isinstance(settings, list):

            if len(settings) == 0:
                raise ValueError("Empty list of init settings supplied")

            if len(settings) < len(clients):
                logger.warning(
                    f"Length of settings list ({len(settings)}) less than number of clients ({len(clients)}), duplicating first supplied settings"
                )

                self._init_settings = settings
                for _ in range(len(clients) - len(settings)):
                    self._init_settings.append(settings[0])

            else:
                logger.info(
                    f"Applying first {len(clients)} entries from supplied init settings (total entries: {len(settings)})"
                )
                self._init_settings = settings[: len(clients)]

        else:
            raise ValueError(f"Unexpected type for settings argument {type(settings)}")

        if len(clients) != len(pump_devices):
            raise ValueError("Inconsistent lengths of clients and devices")

        self._config_filepath = config_filepath
        self._allow_load_history = allow_load_history

        #

        self._pumps: List[BLESmartPump] = []
        for channel, client in enumerate(clients):
            self._pumps.append(
                BLESmartPump(
                    channel=channel,
                    client=client,
                    pump_device=pump_devices[channel],
                    settings=self._init_settings[channel],
                    status_update_interval_s=self._status_update_interval_s,
                    allow_load_history=self._allow_load_history,
                )
            )

    @property
    def device_info(self) -> List[str]:
        info = []
        for idx, pump in enumerate(self._pumps):
            info.append(f"pump {idx}: {pump.info}")
        return info

    @property
    def num_pumps(self) -> int:
        return len(self._pumps)

    def _check_channel(self, channel: int) -> None:
        if channel < 0:
            raise ValueError(f"Channel ({channel}) cannot be negative")

        if channel >= self.num_pumps:
            raise ValueError(
                f"Channel ({channel}) cannot be greater than or equal to {self.num_pumps}"
            )

    async def turn_on(self, channel: int, duration_ms: int = 0) -> None:
        self._check_channel(channel)
        await self._pumps[channel].turn_on(duration_ms=duration_ms)

    async def turn_off(self, channel: int) -> None:
        self._check_channel(channel)
        await self._pumps[channel].turn_off()

    def set_settings(self, channel: int, settings: sp.SmartPumpSettings) -> None:
        self._check_channel(channel)
        self._pumps[channel].settings = settings
        self.save_settings()

    def get_settings(self, channel: int) -> sp.SmartPumpSettings:
        self._check_channel(channel)
        return self._pumps[channel].settings

    def save_settings(self) -> str:
        user_settings = list()
        for channel in range(self.num_pumps):
            user_settings.append(self._pumps[channel].settings)

        return save_user_pumps_config(user_settings)

    def save_history(self) -> str:

        for pump in self._pumps:
            pump.save_history()

        return str(get_history_dir())

    async def get_status(self, channel: int) -> sp.SmartPumpStatus:
        self._check_channel(channel)
        return await self._pumps[channel].status

    def clear_status_logs(self, channel: int) -> None:
        self._check_channel(channel)
        return self._pumps[channel].clear_status_logs()

    def get_status_since(
        self, channel: int, earliest_epoch_time_s: Optional[float]
    ) -> sp.SmartPumpStatusHistory:
        self._check_channel(channel)
        return self._pumps[channel].get_status_since(earliest_epoch_time_s)

    def start(self):
        for pump in self._pumps:
            pump.start()

    async def interrupt(self):
        for pump in self._pumps:
            logger.info(f"interrupting: {pump.channel}")
            await pump.interrupt()

        for pump in self._pumps:
            pump.save_history()


class PumpManagerContext:
    def __init__(
        self,
        settings: pump_manager_settings_type,
        status_update_interval_s: int = 5,
        config_filepath: Optional[pt.Path] = None,
        allow_load_history: bool = False,
        scan_duration_s: float = SCAN_DURATION_S,
    ) -> None:

        self._status_update_interval_s = status_update_interval_s
        self._init_settings = settings
        self._config_filepath = config_filepath
        self._allow_load_history = allow_load_history
        self._scan_duration_s = scan_duration_s

        #

        self._pump_manager: Optional[BLEPumpManager] = None

        self._clients: List[BleakClient] = []

    async def __aenter__(self) -> BLEPumpManager:

        logger.info(f"Scanning for devices for {self._scan_duration_s}s ... ")
        devices = await BleakScanner.discover(timeout=self._scan_duration_s)

        logger.info(f"Found: {len(devices)} device(s):")
        for d in devices:
            logger.info(f"- {d}")

        # Sort results (so that restarts yield ~consistent pump mapping)
        unsorted_pump_devices = [
            device for device in devices if device.name == PUMP_NAME
        ]
        pump_addresses = [device.address for device in unsorted_pump_devices]
        sort_indices = np.argsort(pump_addresses)
        all_pump_devices = [unsorted_pump_devices[int(idx)] for idx in sort_indices]

        logger.info(f"Found: {len(all_pump_devices)} pump(s):")

        pump_devices = []
        for channel, pump_device in enumerate(all_pump_devices):
            logger.info(
                f"Channel {channel}: name {pump_device.name}, address: {pump_device.address}, signal strength: {pump_device.rssi} dBm"
            )

            if pump_device.rssi > MIN_RSSI:
                pump_devices.append(pump_device)
            else:
                logger.warning(
                    f"Rejecting: {channel} as signal is too weak  {pump_device.rssi} <= {MIN_RSSI}"
                )

        if len(pump_devices) == 0:
            logger.warning("No pumps found")

        logger.info(f"Creating {len(pump_devices)} clients")
        self._clients = [BleakClient(pump.address) for pump in pump_devices]

        def disconnect_callback(client: BleakClient) -> None:
            logger.error(f"client disconnected: {client.address}")

        for client in self._clients:
            logger.info(f"Connecting: {client.address} ... ")
            if await client.connect(disconnect_callback=disconnect_callback):
                logger.info("ok")
            else:
                logger.info("FAIL")

        self._pump_manager = BLEPumpManager(
            settings=self._init_settings,
            clients=self._clients,
            pump_devices=pump_devices,
            config_filepath=self._config_filepath,
            status_update_interval_s=self._status_update_interval_s,
            allow_load_history=self._allow_load_history,
        )

        return self._pump_manager

    async def __aexit__(self, exc_type, exc_value, exc_traceback):

        logger.info("Pump manager context shutting down ... ")
        if self._pump_manager:
            await self._pump_manager.interrupt()

        for client in self._clients:
            logger.info(f"Disconnecting: {client.address} ... ")
            if await client.disconnect():
                logger.info("ok")
            else:
                logger.info("FAIL")

        logger.info("Pump manager completed shut down ... ")
