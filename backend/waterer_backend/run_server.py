#!python3

###############################################################
# Imports
###############################################################

import logging

from waterer_backend.config import get_pumps_config
from waterer_backend.pump_manager import PumpManagerContext
from waterer_backend.server import create_app

logging.basicConfig(level=logging.INFO)

###############################################################
# Main
###############################################################


if __name__ == "__main__":

    pumps_config = get_pumps_config()
    app = create_app()

    with PumpManagerContext(
        settings=pumps_config, num_pumps=len(pumps_config)
    ) as pump_manager:

        app.run(debug=False, host="0.0.0.0")
