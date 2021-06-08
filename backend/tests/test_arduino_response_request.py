#!python3

###############################################################
# Imports
###############################################################


import waterer_backend.embedded_arduino as ae
from waterer_backend._test_utils import arduino_fxt, turn_on_request_fxt

###############################################################
# Tests
###############################################################


def test_stop_start(arduino_fxt: ae.EmbeddedArduino):

    assert arduino_fxt is not None


def test_turn_on_request(
    arduino_fxt: ae.EmbeddedArduino, turn_on_request_fxt: ae.Request
):

    arduino_fxt.make_request(turn_on_request_fxt)
