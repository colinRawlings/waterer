#!python3

###############################################################
# Imports
###############################################################

from dataclasses import asdict

from flask import Flask, request
from waterer_backend.config import get_pumps_config
from waterer_backend.pump_manager import PumpManagerContext, get_pump_manager
from waterer_backend.request import Request
from waterer_backend.smart_pump import SmartPumpSettings

###############################################################
# Routings
###############################################################


def create_app() -> Flask:
    app = Flask(__name__)

    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/")
    def main():
        return {"data": get_pump_manager().connection_info}

    @app.route("/turn_on/<channel>")
    def turn_on(channel: str):
        get_pump_manager().turn_on(channel=int(channel))
        return {"data": ""}

    @app.route("/turn_off/<channel>")
    def turn_off(channel: str):
        get_pump_manager().turn_off(channel=int(channel))
        return {"data": ""}

    @app.route("/status/<channel>")
    def get_pump_status(channel: str):
        status = get_pump_manager().get_status(channel=int(channel))
        return {"data": asdict(status)}

    @app.route("/get_status_since/<channel>", methods=["POST"])
    def get_status_since(channel: str):
        if not request.is_json:
            raise RuntimeError("Settings should be provided as json")

        # TODO: request.json["earliest_time"]

        status_history = get_pump_manager().get_status_since(
            channel=int(channel), earliest_epoch_time_s=None
        )
        return {"data": asdict(status_history)}

    @app.route("/save_settings")
    def save_settings():
        saved_filepath = get_pump_manager().save_settings()
        return {"data": saved_filepath}

    @app.route("/settings/<channel>")
    def get_settings(channel: str):
        settings = get_pump_manager().get_settings(channel=int(channel))
        return {"data": asdict(settings)}

    @app.route("/set_settings/<channel>", methods=["POST", "GET"])
    def set_settings(channel: str):

        if not request.is_json:
            raise RuntimeError("Settings should be provided as json")

        new_settings = SmartPumpSettings(**request.json)
        get_pump_manager().set_settings(channel=int(channel), settings=new_settings)

        settings = get_pump_manager().get_settings(channel=int(channel))
        return {"data": asdict(settings)}

    return app
