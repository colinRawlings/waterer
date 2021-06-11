#!python3

###############################################################
# Imports
###############################################################

from waterer_backend._test_utils import turn_on_request_fxt
from waterer_backend.request import Request

###############################################################
# Tests
###############################################################


def test_serialize(turn_on_request_fxt: Request):

    print(turn_on_request_fxt.serialize())


def test_deserialize(turn_on_request_fxt: Request):

    request_str = turn_on_request_fxt.serialize()

    new_request = Request.create(request_str)

    assert new_request == turn_on_request_fxt
