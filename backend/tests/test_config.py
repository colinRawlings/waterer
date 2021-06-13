#!python3

###############################################################
# Imports
###############################################################

import waterer_backend.config as cfg
from waterer_backend.pump_manager import NUM_PUMPS

###############################################################
# Tests
###############################################################


def test_load_config():
    settings_list = cfg.get_pumps_config()

    assert (
        len(settings_list) == NUM_PUMPS
    )  # deviating from this probably won't work yet

    print(settings_list)
