#!python3

###############################################################
# Imports
###############################################################

from dataclasses import dataclass

###############################################################
# Definitions
###############################################################


@dataclass
class Request:
    channel: int
    instruction: str
    data: int

    def __repr__(self) -> str:
        return f"request{{{self.channel},{self.instruction},{self.data}}}"
