# !python3

###############################################################
# Imports
###############################################################


import logging
from typing import Dict, List

import waterer_backend.smart_pump as sp
from waterer_backend.embedded_arduino import EmbeddedArduino

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)

NUM_PUMPS = 3

###############################################################
# Class
###############################################################


class PumpManager:
    def __init__(
        self,
        device: EmbeddedArduino,
        settings: sp.SmartPumpSettings,
        num_pumps: int,
    ) -> None:
        self._num_pumps = num_pumps

        self._pumps = list()  # type: List[sp.SmartPump]
        for channel in range(num_pumps):
            self._pumps.append(
                sp.SmartPump(channel=channel, device=device, settings=settings)
            )

    @property
    def num_pumps(self) -> int:
        return self._num_pumps

    def set_settings(self, settings: sp.SmartPumpSettings) -> None:
        for pump in self._pumps:
            pump.settings = settings

    def get_settings(self, channel: int) -> sp.SmartPumpSettings:
        if channel < 0:
            raise ValueError(f"Channel ({channel}) cannot be negative")

        if channel >= self._num_pumps:
            raise ValueError(
                f"Channel ({channel}) cannot be greater than {self._num_pumps}"
            )

        return self._pumps[channel].settings

    @property
    def statuses(self) -> Dict[int, sp.SmartPumpStatus]:
        statuses = dict()  # type: Dict[int, sp.SmartPumpStatus]
        for pump in self._pumps:
            statuses[pump.channel] = pump.status

        return statuses

    def start(self):

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
