#!python3

###############################################################
# Imports
###############################################################

import asyncio
import logging
from typing import Optional

from aiohttp import web
from waterer_backend.BLE.BLEpump_manager import PumpManagerContext
from waterer_backend.BLE.BLEserver import create_app
from waterer_backend.config import get_pumps_config

###############################################################
# Definitions
###############################################################

logger = logging.getLogger(__name__)
PORT = 5000

RUNNER_KEY = "app_runner"


###############################################################
# Functions
###############################################################


def init_logging() -> None:

    logging.basicConfig(level=logging.INFO)
    aiohttp_logger = logging.getLogger("aiohttp")
    aiohttp_logger.setLevel(logging.ERROR)


###############################################################


def get_runner(app: web.Application) -> Optional[web.AppRunner]:

    if RUNNER_KEY not in app:
        return None

    runner = app[RUNNER_KEY]
    assert isinstance(runner, web.AppRunner)

    return runner


###############################################################


async def run_site(app: web.Application) -> None:

    try:
        runner = web.AppRunner(app)
        app[RUNNER_KEY] = runner

        await runner.setup()
        site = web.TCPSite(runner, port=PORT)
        logger.info(f"Starting site on: http://localhost:{PORT}")
        await site.start()
        logger.info("finished starting site")
    except asyncio.CancelledError:
        logger.info("run_site stop requested during setup ... ")


###############################################################


async def main():
    init_logging()

    pumps_config = get_pumps_config()

    async with PumpManagerContext(
        settings=pumps_config[0], scan_duration_s=10, allow_load_history=True
    ) as manager:

        manager.start()
        app = create_app(manager)
        app["STOP_EVENT"] = asyncio.Event()

        #

        loop = asyncio.get_event_loop()
        task = loop.create_task(run_site(app), name="run_site")

        # wait forever
        try:
            await app["STOP_EVENT"].wait()
        except asyncio.CancelledError:
            logger.info("Stop requested ... ")
        finally:
            if not task.done():
                task.cancel()
                await task
            else:
                logger.debug("Startup task was already done")
            logger.info("Stopping webserver")

            runner = get_runner(app)
            if runner is not None:
                await runner.shutdown()
                await runner.cleanup()

            logger.info("Finished stopping webserver")


###############################################################
# Main
###############################################################

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("User requested stop")
