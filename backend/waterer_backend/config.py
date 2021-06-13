# !python3

###############################################################
# Imports
###############################################################

import json
import logging
import pathlib as pt
import typing as ty

import jsonschema
import pkg_resources as rc
from waterer_backend.smart_pump import SmartPumpSettings

###############################################################
# Logging
###############################################################

_LOGGER = logging.getLogger(__name__)


###############################################################
# Functions
###############################################################


def get_config_dir() -> pt.Path:

    return pt.Path(rc.resource_filename("waterer_backend", "config"))


def get_user_config_filepath() -> pt.Path:

    return get_config_dir() / "user_pump_config.json"


def get_default_config_filepath() -> pt.Path:

    return get_config_dir() / "default_pump_config.json"


def get_config_schema_filepath() -> pt.Path:

    return get_config_dir() / "pump_config_schema.json"


def get_pumps_config() -> ty.List[SmartPumpSettings]:

    if get_user_config_filepath().is_file():
        config_filepath = get_user_config_filepath()
    elif get_default_config_filepath().is_file():
        config_filepath = get_default_config_filepath()
    else:
        raise RuntimeError(f"Failed to find pump config in: {get_config_dir()}")

    _LOGGER.info(f"Loading pump config from: {config_filepath}")

    #

    if not get_config_schema_filepath().is_file():
        raise RuntimeError(
            f"Failed to find pump config schema: {get_config_schema_filepath()}"
        )

    schema_filepath = get_config_schema_filepath()

    with open(schema_filepath, "r") as fh:
        schema = json.load(fh)

    with open(config_filepath, "r") as fh:
        config = json.load(fh)

    validator = jsonschema.Draft7Validator(schema=schema)

    validator.validate(config)

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
