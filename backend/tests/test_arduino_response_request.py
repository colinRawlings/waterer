#!python3

import pytest
import waterer_backend.embedded_arduino as ae

###############################################################
# Fixtures
###############################################################


@pytest.fixture
def arduino():
    with ae.EmbeddedArduinoContext() as ard:
        yield ard


@pytest.fixture
def turn_on_request():
    return ae.Request(1, "turn_on", 100)


###############################################################
# Tests
###############################################################


def test_stop_start(arduino: ae.EmbeddedArduino):

    assert arduino is not None


def test_turn_on_request(arduino: ae.EmbeddedArduino, turn_on_request: ae.Request):

    from time import sleep

    sleep(0.5)

    arduino.make_request(turn_on_request)
