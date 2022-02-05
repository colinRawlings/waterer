#!python3

###############################################################
# Imports
###############################################################


import logging
from dataclasses import asdict

import aiohttp_cors
from aiohttp import web
from waterer_backend import __version__
from waterer_backend.BLE.BLEpump_manager import BLEPumpManager
from waterer_backend.service_logs import get_service_logs
from waterer_backend.smart_pump import SmartPumpSettings

###############################################################
# Definitions
###############################################################

logger = logging.getLogger(__name__)
PUMP_MANAGER_KEY = "pump_manager"

###############################################################
# Functions
###############################################################


def get_pump_manager(request: web.Request) -> BLEPumpManager:

    manager = request.app[PUMP_MANAGER_KEY]
    assert isinstance(manager, BLEPumpManager)

    return manager


###############################################################


def create_app(manager: BLEPumpManager) -> web.Application:

    app = web.Application()
    app[PUMP_MANAGER_KEY] = manager

    routes = web.RouteTableDef()

    @routes.get("/")
    async def main(request: web.Request):

        manager = request.app[PUMP_MANAGER_KEY]
        assert isinstance(get_pump_manager(request), BLEPumpManager)

        return web.json_response(
            {
                "arduino_address": get_pump_manager(request).connection_info,
                "version": __version__,
            }
        )

    @routes.get("/num_pumps")
    async def num_pumps(request: web.Request):
        num_pumps = get_pump_manager(request).num_pumps
        return web.json_response({"data": num_pumps})

    @routes.get("/status/{channel}")
    async def get_pump_status(request: web.Request):
        channel = request.match_info["channel"]
        status = await get_pump_manager(request).get_status(channel=int(channel))
        return web.json_response({"data": asdict(status)})

    @routes.get("/clear_status/{channel}")
    async def clear_status(request: web.Request):
        channel = request.match_info["channel"]
        status = get_pump_manager(request).clear_status_logs(channel=int(channel))
        return web.json_response({"data": ""})

    @routes.get("/get_status_since/{channel}")
    @routes.post("/get_status_since/{channel}")
    async def get_status_since(request: web.Request):
        channel = request.match_info["channel"]

        request_dict = await request.json()

        earliest_time = request_dict["earliest_time"]  # type: ignore

        status_history = get_pump_manager(request).get_status_since(
            channel=int(channel), earliest_epoch_time_s=earliest_time
        )
        return web.json_response({"data": asdict(status_history)})

    @routes.get("/save_settings")
    async def save_settings(request: web.Request):
        saved_filepath = get_pump_manager(request).save_settings()
        return web.json_response({"data": saved_filepath})

    @routes.get("/save_history")
    async def save_history(request: web.Request):
        saved_history_dir = get_pump_manager(request).save_history()
        return web.json_response({"data": saved_history_dir})

    @routes.get("/settings/{channel}")
    async def get_settings(request: web.Request):
        channel = request.match_info["channel"]

        settings = get_pump_manager(request).get_settings(channel=int(channel))
        return web.json_response({"data": asdict(settings)})

    @routes.get("/set_settings/{channel}")
    @routes.post("/set_settings/{channel}")
    async def set_settings(request: web.Request):
        channel = request.match_info["channel"]

        new_settings = SmartPumpSettings(**request.json)  # type: ignore
        get_pump_manager(request).set_settings(
            channel=int(channel), settings=new_settings
        )

        settings = get_pump_manager(request).get_settings(channel=int(channel))
        return web.json_response({"data": asdict(settings)})

    @routes.get("/service_logs/{number_log_lines}")
    async def service_logs(request: web.Request):
        number_log_lines = request.match_info["number_log_lines"]

        logs = get_service_logs(int(number_log_lines))
        return web.json_response({"data": logs})

    app.add_routes(routes)

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(
        app,
        defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        },
    )

    # Configure CORS on all routes.
    for route in list(app.router.routes()):
        cors.add(route)

    return app


###############################################################
