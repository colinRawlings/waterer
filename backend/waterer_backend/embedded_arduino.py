# python3

"""
Wrapper for the arduino implementation of the embedded device 
"""

###############################################################
# Imports
###############################################################


import typing as ty

import pathlib as pt
import json
import serial
import serial.tools.list_ports
from dataclasses import dataclass
import pkg_resources as rc


from time import sleep

import logging

from waterer_backend.request import Request

###############################################################
# Definitions
###############################################################


_LOGGER = logging.getLogger(__name__)
ARDUINO_DESCRIPTION = "Arduino"
BAUD_RATE_CONFIG_KEY = "baud_rate"
STARTUP_MESSAGE = "Arduino ready"

###############################################################
# Class
###############################################################


class EmbeddedArduino:
    def __init__(
        self,
        *,
        port: ty.Optional[str] = None,
        config_filepath: ty.Optional[pt.Path] = None,
    ) -> None:

        self._port = port
        self._config_filepath = config_filepath
        self._device = None

        self._tx_idx = 0

    @property
    def connect_info(self) -> str:

        if self._device is None:
            return "Not connected"

        return f"Device on port: {self._port}"

    def _scan_for_ports(self) -> int:
        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if ARDUINO_DESCRIPTION
            in str(p.description)  # may need tweaking to match new arduinos
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            _LOGGER.warning("Multiple Arduinos found - using the first")

        return arduino_ports[0]

    def connect(self):

        if self._config_filepath is None:
            self._config_filepath = pt.Path(
                rc.resource_filename("waterer_backend", "config.json")
            )

        if not self._config_filepath.is_file():
            raise ValueError(f"Config filepath does not exist: {self._config_filepath}")

        with open(self._config_filepath, "r") as fh:
            config = json.load(fh)

        # TODO: Validate against schema

        if BAUD_RATE_CONFIG_KEY not in config:
            raise ValueError(f"Missing key in config: {BAUD_RATE_CONFIG_KEY}")

        if self._port is None:
            self._port = self._scan_for_ports()

        _LOGGER.info(f"Opening serial port: {self._port}")

        self._device = serial.Serial(port=self._port, baudrate=9600, timeout=5)

        _LOGGER.info(f"Starting to wait for startup message")

        startup_message = self._device.readline().decode()

        _LOGGER.info(f"Recieved: {startup_message}")

        if not startup_message.startswith(STARTUP_MESSAGE):
            raise RuntimeError("Failed to properly start device")

    def make_request(self, request: Request) -> str:

        if self._device is None:
            raise RuntimeError("Device not initialized")

        if not self._device.is_open:
            raise RuntimeError("Device not open")

        self._device.write(f"{request}\r\n".encode())

        response = self._device.readline().decode()

        _LOGGER.info(f"{self._tx_idx}: {response}")
        self._tx_idx += 1

        return response

    def get_voltage(self, channel: int) -> float:

        voltage_request = Request(channel, "get_voltage", 100)
        request_response = self.make_request(voltage_request)

        def report_error() -> None:
            msg = f"get_voltage failed: {request_response}"
            _LOGGER.error(msg)
            raise RuntimeError(msg)

        if "ERROR" in request_response:
            report_error()

        response_str = request_response.split("response")

        if len(response_str) != 2:
            report_error()

        return json.loads(response_str[1])["data"]


###############################################################
# Main
###############################################################


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    ard = EmbeddedArduino()
    on_request = Request(1, "turn_on", 100)
    off_request = Request(1, "turn_off", 100)
    voltage_request = Request(1, "get_voltage", 100)

    ard.connect()

    while True:
        ard.make_request(on_request)

        sleep(0.5)

        ard.make_request(off_request)

        sleep(0.5)

        print(f"voltage: {ard.get_voltage(1)}")

        sleep(0.5)

