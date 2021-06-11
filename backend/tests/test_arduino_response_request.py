#!python3

###############################################################
# Imports
###############################################################


import waterer_backend.embedded_arduino as ae
from waterer_backend._test_utils import arduino_fxt, turn_on_request_fxt
from waterer_backend.request import Request
from waterer_backend.response import Response

###############################################################
# Tests
###############################################################


def test_stop_start(arduino_fxt: ae.EmbeddedArduino):

    assert arduino_fxt is not None


def test_turn_on_request(arduino_fxt: ae.EmbeddedArduino, turn_on_request_fxt: Request):

    response = arduino_fxt.make_request(turn_on_request_fxt)
    assert response.success


def test_turn_off_request(arduino_fxt: ae.EmbeddedArduino):

    response = arduino_fxt.make_request(Request(1, "turn_off", 0))
    assert response.success


def test_bad_json(arduino_fxt: ae.EmbeddedArduino):

    response_str = arduino_fxt.send_str('{"channel": 1')

    response = Response.create(response_str)

    assert response.success == False
    assert response.message == "Request de-serialization failed: Deserialize failed."


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
