#!python3

###############################################################
# Imports
###############################################################

from waterer_backend._test_utils import turn_on_response_fxt
from waterer_backend.response import Response

###############################################################
# Tests
###############################################################


def test_serialize(turn_on_response_fxt: Response):

    turn_on_response_fxt.serialize()


def test_deserialize(turn_on_response_fxt: Response):

    response_str = turn_on_response_fxt.serialize()

    new_response = Response.create(response_str)

    assert new_response == turn_on_response_fxt
