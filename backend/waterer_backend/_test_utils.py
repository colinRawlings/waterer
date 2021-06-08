#!python3

import pytest
import waterer_backend.embedded_arduino as ae

###############################################################
# Fixtures
###############################################################


@pytest.fixture
def arduino_fxt():
    with ae.EmbeddedArduinoContext() as ard:
        yield ard


@pytest.fixture
def turn_on_request_fxt():
    return ae.Request(1, "turn_on", 100)
