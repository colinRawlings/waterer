#!python3

###############################################################
# Imports
###############################################################

import subprocess as sp

###############################################################
# Definitions
###############################################################

SERVICE_NAME = "waterer_backend.service"


###############################################################
# Function
###############################################################


def get_service_logs(num_lines: int = 100) -> str:

    cmd = ["journalctl", "-u", SERVICE_NAME, "-n", str(num_lines)]

    result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE)

    return f'{result.stdout.decode(encoding="ascii", errors="ignore")}\n{result.stderr.decode(encoding="ascii", errors="ignore")}'
