from flask import Flask

from waterer_backend.embedded_arduino import EmbeddedArduino, Request

app = Flask(__name__)
ard = None


@app.route("/")
def main():
    if ard is None:
        return "No ard!"

    return ard.connect_info


@app.route("/turn_on")
def turn_on():
    if ard is None:
        return "No ard!"

    ard.make_request(Request(1, "turn_on", 100))

    return "turned on"


@app.route("/turn_off")
def turn_off():
    if ard is None:
        return "No ard!"

    ard.make_request(Request(1, "turn_off", 100))

    return "turned off"


if __name__ == "__main__":
    ard = EmbeddedArduino()
    ard.connect()

    app.run()
