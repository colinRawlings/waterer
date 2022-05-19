# !python3

###############################################################
# Imports
###############################################################

import json
import logging
import pathlib as pt
import typing as ty
from dataclasses import asdict

import jsonschema
import pkg_resources as rc
from waterer_backend.models import SmartPumpSettings

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)


###############################################################
# Functions
###############################################################


def get_config_dir() -> pt.Path:

    return pt.Path(rc.resource_filename("waterer_backend", "config"))


def get_history_dir() -> pt.Path:

    return pt.Path(rc.resource_filename("waterer_backend", "history"))


def get_history_filepath(channel: int) -> pt.Path:

    return get_history_dir() / f"pump_{channel}_history.json"


def get_user_config_filepath() -> pt.Path:

    return get_config_dir() / "user_pump_config.json"


def get_default_config_filepath() -> pt.Path:

    return get_config_dir() / "default_pump_config.json"


def save_user_pumps_config(settings_list: ty.List[SmartPumpSettings]) -> str:

    pumps_config = []

    for channel, settings in enumerate(settings_list):
        pumps_config.append(dict(channel=channel, settings=asdict(settings)))

    filepath = get_user_config_filepath()
    with open(filepath, "w") as fh:
        json.dump(pumps_config, fh, indent=4)

    return str(filepath)


def get_pumps_config(use_default: bool = False) -> ty.List[SmartPumpSettings]:

    if get_user_config_filepath().is_file():
        config_filepath = get_user_config_filepath()
    elif get_default_config_filepath().is_file():
        config_filepath = get_default_config_filepath()
    else:
        raise RuntimeError(f"Failed to find pump config in: {get_config_dir()}")

    _LOGGER.info(f"Loading pump config from: {config_filepath}")

    #

    with open(config_filepath, "r") as fh:
        config = json.load(fh)

    #

    expected_channels = {channel for channel in range(len(config))}
    found_channels = set()  # type: ty.Set[int]

    optional_settings_list = [
        None for _ in range(len(config))
    ]  # type: ty.List[ty.Optional[SmartPumpSettings]]

    for channel_settings in config:
        found_channels.add(channel_settings["channel"])

        settings = SmartPumpSettings(**channel_settings["settings"])

        optional_settings_list[channel_settings["channel"]] = settings

    if not expected_channels == found_channels:
        raise RuntimeError(
            "Loaded config does not contain a contiguous set of channel settings"
        )

    settings_list = list()  # type: ty.List[SmartPumpSettings]

    for settings in optional_settings_list:
        assert settings is not None
        settings_list.append(settings)

    return settings_list
