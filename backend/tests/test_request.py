#!python3

###############################################################
# Imports
###############################################################

import waterer_backend.embedded_arduino as ae
from waterer_backend._test_utils import turn_on_request_fxt

###############################################################
# Tests
###############################################################


def test_serialize(turn_on_request_fxt: ae.Request):
    print(f"{turn_on_request_fxt}")
