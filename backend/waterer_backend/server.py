#!python3

###############################################################
# Imports
###############################################################


import waterer_backend.embedded_singleton as es
from flask import Flask
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

    ard = es.get_embedded_device()
    if ard is None:
        return "No ard!"

    return {"data": ard.connect_info}


@app.route("/turn_on")
def turn_on():
    ard = es.get_embedded_device()

    if ard is None:
        return "No ard!"

    response = ard.make_request(Request(1, "turn_on", 100))

    return {"data": response}


@app.route("/turn_off")
def turn_off():
    ard = es.get_embedded_device()

    if ard is None:
        return "No ard!"

    response = ard.make_request(Request(1, "turn_off", 100))

    return {"data": response}


@app.route("/get_voltage")
def get_voltage():
    ard = es.get_embedded_device()

    if ard is None:
        return "No ard!"

    response = ard.get_voltage(1)

    return {"data": response}


###############################################################
# Main
###############################################################


if __name__ == "__main__":
    app.run(debug=True)
