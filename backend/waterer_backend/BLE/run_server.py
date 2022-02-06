#!python3

###############################################################
# Imports
###############################################################

import asyncio
import logging

from aiohttp import web
from waterer_backend.BLE.BLEpump_manager import PumpManagerContext
from waterer_backend.BLE.BLEserver import create_app
from waterer_backend.config import get_pumps_config

###############################################################
# Definitions
###############################################################

logger = logging.getLogger(__name__)
PORT = 5000


###############################################################
# Functions
###############################################################


def init_logging() -> None:

    logging.basicConfig(level=logging.INFO)
    aiohttp_logger = logging.getLogger("aiohttp")
    aiohttp_logger.setLevel(logging.ERROR)


###############################################################


async def run_site(app: web.Application) -> None:
    try:
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, port=PORT)
        logger.info(f"Starting site on: http://localhost:{PORT}")
        await site.start()
        logger.info("finished starting site")
    except asyncio.CancelledError:
        logger.info("run_site stop requested ... ")


###############################################################


async def main():
    init_logging()

    pumps_config = get_pumps_config()

    async with PumpManagerContext(
        settings=pumps_config[0], scan_duration_s=10
    ) as manager:

        manager.start()
        app = create_app(manager)

        #

        loop = asyncio.get_event_loop()
        task = loop.create_task(run_site(app))

        # wait forever
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            logger.info("Stop requested ... ")
            if not task.done():
                task.cancel()
                await task


###############################################################
# Main
###############################################################

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("User requested stop")
