# python3

"""
Wrapper for the arduino implementation of the embedded device
"""

###############################################################
# Imports
###############################################################

import datetime
import json
import logging
import os
import pathlib as pt
import typing as ty
from random import random
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

ALLOW_FAKE_DATA_KEY = "WATERER_FAKE_DATA"

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

        version_str = self.get_version()

        return f"Device on port: {self._port}, Embedded S/W Version: {version_str}"

    def _scan_for_ports(self) -> str:

        arduino_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if (
                (ARDUINO_DESCRIPTION in str(p.description))
                or (p.description.startswith("ttyACM"))  # type: ignore
            )
        ]
        if not arduino_ports:
            raise IOError("No Arduino found")
        if len(arduino_ports) > 1:
            _LOGGER.warning("Multiple Arduinos found - using the first")

        return arduino_ports[0]

    def _open_serial_port(self):

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

            try:
                if self._port is None:
                    self._port = self._scan_for_ports()

                _LOGGER.info(f"Opening serial port: {self._port}")

                self._device = serial.Serial(
                    port=self._port, baudrate=config[BAUD_RATE_CONFIG_KEY], timeout=5
                )

                _LOGGER.info(f"Starting to wait for startup message")

                startup_message = self._device.readline().decode()

                _LOGGER.info(f"Recieved: {startup_message}")

            except Exception as e:
                if ALLOW_FAKE_DATA_KEY in os.environ:
                    self._device = None
                    _LOGGER.warning(
                        f"Encountered {e} during connect, ignoring as found {ALLOW_FAKE_DATA_KEY} in environment variables"
                    )
                else:
                    raise e

    def get_version(self) -> str:

        response = self.make_request(Request(0, "get_version", 0))
        if response.success:
            return f"{response.data:.1f}"
        else:
            _LOGGER.error(f"Failed to check version: {response.message}")
            return "UNKNOWN"

    def log_version(self):

        version_str = self.get_version()

        _LOGGER.info(f"Embedded version: {version_str}")

    def connect(self):

        self._open_serial_port()

        self.log_version()

    def disconnect(self):

        with self._lock:

            if self._device is None:
                _LOGGER.warning("No device to disconnect")
                return

            if not self._device.is_open:
                _LOGGER.warning("Device not open - no need to disconnect")

            self._device.close()

            _LOGGER.info("Closed device")

    def _generate_fake_data(self, request_str: str) -> str:

        _LOGGER.warning(f"Faking response to request: {request_str}")

        request = Request.create(request_str)
        assert request.id is not None

        response = Response(
            request.id, request.channel, request.instruction, True, 0, "fake"
        )

        if request.instruction == "get_voltage":
            response.data = 5 * random()
        elif request.instruction == "get_state":
            a = datetime.datetime.now()
            response.data = float(a.second < 30)

        return response.serialize()

    def send_str(self, request_str) -> str:
        """
        returns response_str
        """

        with self._lock:

            if self._device is None:

                if ALLOW_FAKE_DATA_KEY in os.environ:
                    return self._generate_fake_data(request_str)

                raise RuntimeError("Device not initialized")

            if not self._device.is_open:
                raise RuntimeError("Device not open")

            # n.b. best effort (won't work if device is busy creating output at time of request)
            self._device.flushInput()
            self._device.flushOutput()

            self._device.write(f"{request_str}\r\n".encode())

            response_str = self._device.readline().decode()

            return response_str

    def make_request(self, request: Request) -> Response:

        response_str = self.send_str(request_str=request.serialize())

        tx_info = f"{self._tx_idx} <{request.serialize()}>: {response_str}"
        _LOGGER.debug(tx_info)
        self._tx_idx += 1

        response = Response.create(response_str=response_str)

        if not response.id == request.id:
            raise RuntimeError(
                f"Request ({request.id})/Reponse ({response.id}) id's do not match\n{tx_info}"
            )

        return response
