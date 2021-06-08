# python3

"""
Wrapper for the arduino implementation of the embedded device
"""

###############################################################
# Imports
###############################################################


import json
import logging
import pathlib as pt
import typing as ty
from dataclasses import dataclass
from time import sleep

import pkg_resources as rc
import serial
import serial.tools.list_ports
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

    def disconnect(self):

        if self._device is None:
            _LOGGER.warning("No device to disconnect")

        if not self._device.is_open:
            _LOGGER.warning("Device not open - no need to disconnect")

        self._device.close()

        _LOGGER.info("Closed device")

    def make_request(self, request: Request) -> str:

        if self._device is None:
            raise RuntimeError("Device not initialized")

        if not self._device.is_open:
            raise RuntimeError("Device not open")

        # n.b. best effort (won't work if device is busy creating data at time of request)
        self._device.flushInput()
        self._device.flushOutput()

        self._device.write(f"{request}\r\n".encode())

        response = self._device.readline().decode()

        _LOGGER.info(f"{self._tx_idx} <{request}>: {response}")
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


class EmbeddedArduinoContext:
    def __init__(
        self,
        port: ty.Optional[str] = None,
        config_filepath: ty.Optional[pt.Path] = None,
    ) -> None:
        self._arduino = None

        self._port = port
        self._config_filepath = config_filepath

    def __enter__(self) -> EmbeddedArduino:

        self._arduino = EmbeddedArduino(
            port=self._port, config_filepath=self._config_filepath
        )
        self._arduino.connect()

        return self._arduino

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._arduino.disconnect()
