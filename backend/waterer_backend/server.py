#!python3

###############################################################
# Imports
###############################################################


from flask import Flask
from waterer_backend.config import get_pumps_config
from waterer_backend.pump_manager import PumpManagerContext, get_pump_manager
from waterer_backend.request import Request

###############################################################
# Routings
###############################################################


app = Flask(__name__)


@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response


@app.route("/")
def main():

    pump_manager = get_pump_manager()

    return {"data": ard.connect_info}


@app.route("/turn_on/<channel>")
def turn_on():
    pump_manager = get_pump_manager()

    response = ard.make_request(Request(1, "turn_on", 100))

    return {"data": response}


@app.route("/turn_off/<channel>")
def turn_off():
    pump_manager = get_pump_manager()

    response = ard.make_request(Request(1, "turn_off", 100))

    return {"data": response}


@app.route("/get_pump_state/<channel>")
def get_voltage():
    pump_manager = get_pump_manager()

    response = ard.get_voltage(1)

    return {"data": response}


@app.route("/get_status/<channel>")
def get_status():
    pump_manager = get_pump_manager()

    response = ard.get_voltage(1)

    return {"data": response}


@app.route("/get_settings/<channel>")
def get_settings():
    pump_manager = get_pump_manager()

    response = ard.get_voltage(1)

    return {"data": response}


@app.route("/set_settings/<channel>")
def set_settings():
    pump_manager = get_pump_manager()

    response = ard.get_voltage(1)

    return {"data": response}


###############################################################
# Main
###############################################################


if __name__ == "__main__":

    pump_config = get_pumps_config()

    with PumpManagerContext(
        settings=pump_config, num_pumps=len(pump_config)
    ) as pump_manager:

        app.run(debug=False)
