# !python3

###############################################################
# Imports
###############################################################

import pathlib as pt
import socket

from jinja2 import Environment, FileSystemLoader, select_autoescape

###############################################################
# Definitions
###############################################################


_DIR = pt.Path(__name__).parent

###############################################################
# Functions
###############################################################


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


###############################################################
# Main
###############################################################

if __name__ == "__main__":

    env = Environment(
        loader=FileSystemLoader(_DIR / "templates"), autoescape=select_autoescape()
    )

    template = env.get_template("env.js")

    output_files = (_DIR / "dist" / "waterer" / "env.js", _DIR / "src" / "env.js")

    for output_file in output_files:
        with open(output_file, "w") as fh:
            fh.write(template.render(current_ip=str(get_ip())))
