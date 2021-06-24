# !python3

###############################################################
# Imports
###############################################################


import logging
import pathlib as pt
from typing import Dict, List, Optional, Union

import waterer_backend.smart_pump as sp
from waterer_backend.config import save_user_pumps_config
from waterer_backend.embedded_arduino import EmbeddedArduino

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)

NUM_PUMPS = 3


global _GLOBAL_pump_manager
_GLOBAL_pump_manager = None


###############################################################
# Definitions
###############################################################


###############################################################
# Functions
###############################################################


###############################################################
# Class
###############################################################

pump_manager_settings_type = Union[List[sp.SmartPumpSettings], sp.SmartPumpSettings]


class PumpManager:
    def __init__(
        self,
        settings: pump_manager_settings_type,
        num_pumps: int,
        status_update_interval_s: int = 5,
        port: Optional[str] = None,
        config_filepath: Optional[pt.Path] = None,
    ) -> None:
        self._num_pumps = num_pumps
        self._status_update_interval_s = status_update_interval_s

        if isinstance(settings, sp.SmartPumpSettings):
            self._init_settings = [settings for _ in range(num_pumps)]
        elif isinstance(settings, list):
            if len(settings) != num_pumps:
                raise ValueError(
                    f"Length of settings list ({len(settings)}) does not match num_pumps ({num_pumps})"
                )
            self._init_settings = settings
        else:
            raise ValueError(f"Unexpected type for settings argument {type(settings)}")

        self._port = port
        self._config_filepath = config_filepath
        self._device = None  # type: Optional[EmbeddedArduino]

    @property
    def num_pumps(self) -> int:
        return self._num_pumps

    @property
    def connection_info(self) -> str:

        if self._device is None:
            raise RuntimeError("Device not initialized did you call start()")

        return self._device.connection_info

    def _check_channel(self, channel: int) -> None:
        if channel < 0:
            raise ValueError(f"Channel ({channel}) cannot be negative")

        if channel >= self._num_pumps:
            raise ValueError(
                f"Channel ({channel}) cannot be greater than {self._num_pumps}"
            )

    def turn_on(self, channel: int) -> None:
        self._check_channel(channel)
        self._pumps[channel].turn_on()

    def turn_off(self, channel: int) -> None:
        self._check_channel(channel)
        self._pumps[channel].turn_off()

    def set_settings(self, channel: int, settings: sp.SmartPumpSettings) -> None:
        self._check_channel(channel)
        self._pumps[channel].settings = settings

    def get_settings(self, channel: int) -> sp.SmartPumpSettings:
        self._check_channel(channel)
        return self._pumps[channel].settings

    def save_settings(self) -> str:
        user_settings = list()
        for channel in range(self._num_pumps):
            user_settings.append(self._pumps[channel].settings)

        return save_user_pumps_config(user_settings)

    def get_status(self, channel: int) -> sp.SmartPumpStatus:
        self._check_channel(channel)
        return self._pumps[channel].status

    def get_status_since(
        self, channel: int, earliest_epoch_time_s: Optional[float]
    ) -> sp.SmartPumpStatusHistory:
        self._check_channel(channel)
        return self._pumps[channel].get_status_since(earliest_epoch_time_s)

    def start(self):

        _LOGGER.info(f"Creating device")

        if self._device is not None:
            raise RuntimeError(
                "Device already exists did -you previously call start()?"
            )

        try:
            self._device = EmbeddedArduino(
                port=self._port, config_filepath=self._config_filepath
            )
            self._device.connect()
        except Exception as e:
            _LOGGER.error(f"Failed to create device: {repr(e)}")

        _LOGGER.info(f"Creating {self._num_pumps} pumps")

        self._pumps = list()  # type: List[sp.SmartPump]
        for channel in range(self._num_pumps):
            self._pumps.append(
                sp.SmartPump(
                    channel=channel,
                    device=self._device,
                    settings=self._init_settings[channel],
                    status_update_interval_s=self._status_update_interval_s,
                )
            )

        _LOGGER.info(f"Starting {self._num_pumps} pumps")
        for pump in self._pumps:
            pump.start()

    def interrupt(self):

        _LOGGER.info(f"Interrupting {self._num_pumps} pumps")

        for pump in self._pumps:
            pump.interrupt()

        _LOGGER.info(f"Joining {self._num_pumps} pumps")

        for pump in self._pumps:
            pump.join()

        _LOGGER.info(f"Stopped {self._num_pumps} pumps")

        assert self._device is not None
        self._device.disconnect()


###############################################################
# Context
###############################################################


def init_pump_manager(
    settings: pump_manager_settings_type,
    num_pumps: int,
    status_update_interval_s: int = 5,
    port: Optional[str] = None,
    config_filepath: Optional[pt.Path] = None,
) -> PumpManager:

    global _GLOBAL_pump_manager
    _GLOBAL_pump_manager = PumpManager(
        settings=settings,
        num_pumps=num_pumps,
        port=port,
        config_filepath=config_filepath,
        status_update_interval_s=status_update_interval_s,
    )

    _GLOBAL_pump_manager.start()

    return _GLOBAL_pump_manager


def get_pump_manager() -> PumpManager:
    global _GLOBAL_pump_manager
    assert _GLOBAL_pump_manager is not None

    return _GLOBAL_pump_manager


class PumpManagerContext:
    def __init__(
        self,
        settings: pump_manager_settings_type,
        num_pumps: int,
        status_update_interval_s: int = 5,
        port: Optional[str] = None,
        config_filepath: Optional[pt.Path] = None,
    ) -> None:
        self._num_pumps = num_pumps
        self._status_update_interval_s = status_update_interval_s
        self._init_settings = settings
        self._port = port
        self._config_filepath = config_filepath

    def __enter__(self) -> PumpManager:

        return init_pump_manager(
            settings=self._init_settings,
            num_pumps=self._num_pumps,
            status_update_interval_s=self._status_update_interval_s,
            port=self._port,
            config_filepath=self._config_filepath,
        )

    def __exit__(self, exc_type, exc_value, exc_traceback):
        get_pump_manager().interrupt()
