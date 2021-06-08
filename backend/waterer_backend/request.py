#!python3

###############################################################
# Imports
###############################################################

from dataclasses import asdict, dataclass

###############################################################
# Definitions
###############################################################


@dataclass
class Request:
    channel: int
    instruction: str
    data: int

    def __repr__(self) -> str:
        return f"{dict(request=asdict(self))}"
