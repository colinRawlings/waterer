# python3

"""
Implement device as singleton owned by this module

- n.b. could further develop abstraction to non-arduino implementations
as required
"""

###############################################################
# Imports
###############################################################

import pathlib as pt
import typing as ty

from waterer_backend.embedded_arduino import EmbeddedArduino

###############################################################
# Definitions
###############################################################

global _GLOBAL_ard
_GLOBAL_ard = None


###############################################################
# Functions
###############################################################


def init_embedded_device(
    port: ty.Optional[str] = None,
    config_filepath: ty.Optional[pt.Path] = None,
) -> EmbeddedArduino:

    global _GLOBAL_ard
    assert _GLOBAL_ard is None

    _GLOBAL_ard = EmbeddedArduino(port=port, config_filepath=config_filepath)
    _GLOBAL_ard.connect()

    return _GLOBAL_ard


###############################################################


def get_embedded_device() -> EmbeddedArduino:

    global _GLOBAL_ard
    assert _GLOBAL_ard is not None

    return _GLOBAL_ard


###############################################################
# Classes
###############################################################


class EmbeddedDeviceContext:
    def __init__(
        self,
        port: ty.Optional[str] = None,
        config_filepath: ty.Optional[pt.Path] = None,
    ) -> None:

        self._port = port
        self._config_filepath = config_filepath

    def __enter__(self) -> EmbeddedArduino:

        return init_embedded_device(
            port=self._port, config_filepath=self._config_filepath
        )

    def __exit__(self, exc_type, exc_value, exc_traceback):
        global _GLOBAL_ard

        if _GLOBAL_ard is not None:
            _GLOBAL_ard.disconnect()
            _GLOBAL_ard = None
