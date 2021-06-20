#!python3

###############################################################
# Imports
###############################################################

from time import perf_counter, sleep

import waterer_backend.embedded_arduino as ae
from waterer_backend._test_utils import arduino_fxt, turn_on_request_fxt
from waterer_backend.request import Request
from waterer_backend.response import Response

###############################################################
# Tests
###############################################################


def test_stop_start(arduino_fxt: ae.EmbeddedArduino):

    assert arduino_fxt is not None


def test_turn_on_off_request(
    arduino_fxt: ae.EmbeddedArduino, turn_on_request_fxt: Request
):

    response = arduino_fxt.make_request(Request(1, "turn_on", 0))
    assert response.success

    response = arduino_fxt.make_request(Request(1, "get_state", 0))
    assert response.success
    assert response.data == 1

    response = arduino_fxt.make_request(Request(1, "turn_off", 0))
    assert response.success

    response = arduino_fxt.make_request(Request(1, "get_state", 0))
    assert response.success
    assert response.data == 0


def test_turn_on_for_request(
    arduino_fxt: ae.EmbeddedArduino, turn_on_request_fxt: Request
):

    on_duration_s = 5
    margin_s = 1
    channel = 1

    response = arduino_fxt.make_request(Request(channel, "turn_on", on_duration_s))
    assert response.success

    T0 = perf_counter()

    while perf_counter() - T0 < on_duration_s - margin_s:
        response = arduino_fxt.make_request(Request(channel, "get_state", 0))
        assert response.success
        assert response.data == 1

    sleep(2 * margin_s)

    response = arduino_fxt.make_request(Request(channel, "get_state", 0))
    assert response.success
    assert response.data == 0


def test_turn_on_for_long_request(arduino_fxt: ae.EmbeddedArduino):

    duration = 600

    response = arduino_fxt.make_request(Request(1, "turn_on", duration))
    assert response.success
    assert response.data == duration


def test_turn_off_request(arduino_fxt: ae.EmbeddedArduino):

    response = arduino_fxt.make_request(Request(1, "turn_off", 0))
    assert response.success


def test_bad_channel(arduino_fxt: ae.EmbeddedArduino):

    response = arduino_fxt.make_request(Request(42, "turn_off", 0))
    assert not response.success
    assert "Invalid channel" in response.message


def test_bad_json(arduino_fxt: ae.EmbeddedArduino):

    response_str = arduino_fxt.send_str('{"channel": 1')

    response = Response.create(response_str)

    assert response.success == False
    assert "Deserialize failed" in response.message


def test_incomplete_request(arduino_fxt: ae.EmbeddedArduino):

    response_str = arduino_fxt.send_str('{"channel": 1, "data": 100, "id": 9860}')

    response = Response.create(response_str)

    assert response.success == False
    assert "Missing instruction key" in response.message


def test_bad_instruction(arduino_fxt: ae.EmbeddedArduino):

    response_str = arduino_fxt.send_str(
        '{"channel": 1, "instruction": "foo", "data": 100, "id": 9860}'
    )

    response = Response.create(response_str)

    assert response.success == False
    assert response.message == "Error: Unrecognized instruction: foo"
