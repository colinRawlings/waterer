#!python3

from random import randint

import pytest
import waterer_backend.embedded_arduino as ae
from waterer_backend.request import Request
from waterer_backend.response import Response

###############################################################
# Fixtures
###############################################################


@pytest.fixture
def arduino_fxt():
    with ae.EmbeddedArduinoContext() as ard:
        yield ard


@pytest.fixture
def turn_on_request_fxt():
    return Request(channel=1, instruction="turn_on", data=0)


@pytest.fixture
def turn_on_response_fxt():
    return Response(1, 1, "turn_on", True, 100, "")
