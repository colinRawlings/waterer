#!python3

###############################################################
# Imports
###############################################################

import json
from copy import deepcopy
from dataclasses import asdict
from time import sleep
from typing import List

import pytest
from flask.testing import FlaskClient
from waterer_backend.config import get_pumps_config
from waterer_backend.pump_manager import PumpManagerContext
from waterer_backend.server import create_app
from waterer_backend.smart_pump import (
    SmartPumpSettings,
    SmartPumpStatus,
    SmartPumpStatusHistory,
)

###############################################################
# Fixtures
###############################################################


@pytest.fixture
def pumps_config():
    return get_pumps_config(use_default=True)


@pytest.fixture
def server_client(pumps_config):
    app = create_app()

    with PumpManagerContext(
        settings=pumps_config, num_pumps=len(pumps_config), status_update_interval_s=1
    ) as pump_manager:
        with app.test_client() as client:
            yield client


###############################################################
# Server
###############################################################


def test_start_stop(server_client: FlaskClient):
    response = server_client.get("/")
    assert response.status_code == 200

    data = json.loads(response.data.decode())
    assert "Device on port" in data["data"]


def test_turn_on_off(server_client: FlaskClient):
    response = server_client.get("/turn_on/2")
    assert response.status_code == 200

    response = server_client.get("/status/2")
    assert response.status_code == 200

    data = json.loads(response.data.decode())
    assert data["data"]["pump_running"]

    response = server_client.get("/turn_off/2")
    assert response.status_code == 200

    response = server_client.get("/status/2")
    assert response.status_code == 200

    data = json.loads(response.data.decode())
    assert not data["data"]["pump_running"]


def test_settings(server_client: FlaskClient):
    response = server_client.get("/settings/2")
    assert response.status_code == 200

    settings = SmartPumpSettings(**json.loads(response.data.decode())["data"])


def test_status(server_client: FlaskClient):
    response = server_client.get("/status/2")
    assert response.status_code == 200

    status = SmartPumpStatus(**json.loads(response.data.decode())["data"])


def test_status_history(server_client: FlaskClient):

    run_time_s = 5
    sample_tolerance_s = 2

    sleep(run_time_s)

    response = server_client.get("/get_status_since/2", json=dict(earliest_time=None))
    assert response.status_code == 200

    status_history = SmartPumpStatusHistory(
        **json.loads(response.data.decode())["data"]
    )

    assert (
        abs(len(status_history.rel_humidity_V_epoch_time) - run_time_s)
        <= sample_tolerance_s
    )

    sleep(run_time_s)

    response = server_client.get(
        "/get_status_since/2",
        json=dict(earliest_time=status_history.rel_humidity_V_epoch_time[-1]),
    )
    assert response.status_code == 200

    status_history_2 = SmartPumpStatusHistory(
        **json.loads(response.data.decode())["data"]
    )

    assert (
        abs(len(status_history_2.rel_humidity_V_epoch_time) - run_time_s)
        <= sample_tolerance_s
    )

    assert (
        status_history_2.rel_humidity_V_epoch_time[0]
        >= status_history.rel_humidity_V_epoch_time[-1]
    )


def test_set_settings(server_client: FlaskClient):
    response = server_client.get("/settings/2")
    assert response.status_code == 200
    original_settings = SmartPumpSettings(**json.loads(response.data.decode())["data"])

    new_settings = deepcopy(original_settings)
    assert new_settings == original_settings

    new_settings.dry_humidity_V -= 1
    assert new_settings != original_settings

    #

    response = server_client.get("/set_settings/2", json=asdict(new_settings))
    assert response.status_code == 200

    response = server_client.get("/settings/2")
    assert response.status_code == 200
    settings = SmartPumpSettings(**json.loads(response.data.decode())["data"])

    assert settings == new_settings
