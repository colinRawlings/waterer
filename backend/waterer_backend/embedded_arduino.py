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
from threading import Lock

import pkg_resources as rc
import serial
import serial.tools.list_ports
from waterer_backend.request import Request
from waterer_backend.response import Response

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
        self._lock = Lock()

        self._tx_idx = 0

    @property
    def connection_info(self) -> str:

        if self._device is None:
            return "Not connected"

        return f"Device on port: {self._port}"

    def _scan_for_ports(self) -> int:

        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if (
                (ARDUINO_DESCRIPTION in str(p.description))
                or (p.description.startswith("ttyACM"))
            )  # type: ignore
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            _LOGGER.warning("Multiple Arduinos found - using the first")

        return arduino_ports[0]

    def connect(self):

        with self._lock:
            if self._config_filepath is None:
                self._config_filepath = pt.Path(
                    rc.resource_filename(
                        "waterer_backend", str(pt.Path("config") / "device_config.json")
                    )
                )

            if not self._config_filepath.is_file():
                raise ValueError(
                    f"Config filepath does not exist: {self._config_filepath}"
                )

            with open(self._config_filepath, "r") as fh:
                config = json.load(fh)

            # TODO: Validate against schema

            if BAUD_RATE_CONFIG_KEY not in config:
                raise ValueError(f"Missing key in config: {BAUD_RATE_CONFIG_KEY}")

            if self._port is None:
                self._port = self._scan_for_ports()

            _LOGGER.info(f"Opening serial port: {self._port}")

            self._device = serial.Serial(
                port=self._port, baudrate=config[BAUD_RATE_CONFIG_KEY], timeout=5
            )

            _LOGGER.info(f"Starting to wait for startup message")

            startup_message = self._device.readline().decode()

            _LOGGER.info(f"Recieved: {startup_message}")

            if not startup_message.startswith(STARTUP_MESSAGE):
                raise RuntimeError("Failed to properly start device")

    def disconnect(self):

        with self._lock:

            if self._device is None:
                _LOGGER.warning("No device to disconnect")

            if not self._device.is_open:
                _LOGGER.warning("Device not open - no need to disconnect")

            self._device.close()

            _LOGGER.info("Closed device")

    def send_str(self, request_str) -> str:
        """Low level method useful for testing"""

        with self._lock:

            if self._device is None:
                raise RuntimeError("Device not initialized")

            if not self._device.is_open:
                raise RuntimeError("Device not open")

            # n.b. best effort (won't work if device is busy creating output at time of request)
            self._device.flushInput()
            self._device.flushOutput()

            self._device.write(f"{request_str}\r\n".encode())

            response_str = self._device.readline().decode()

            _LOGGER.debug(f"{self._tx_idx} <{request_str}>: {response_str}")
            self._tx_idx += 1

            return response_str

    def make_request(self, request: Request) -> Response:

        response_str = self.send_str(request_str=request.serialize())

        response = Response.create(response_str=response_str)

        if not response.id == request.id:
            raise RuntimeError("Request/Reponse id's do not match")

        return response
