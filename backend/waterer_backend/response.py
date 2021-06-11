#!python3

###############################################################
# Imports
###############################################################

import json
import pathlib as pt
from dataclasses import asdict, dataclass

import jsonschema
import pkg_resources as rc

###############################################################
# Definitions
###############################################################

MAX_LENGTH = 200  # Must stay in sync with value in HwDefs.h

###############################################################
# Classes
###############################################################


@dataclass
class Response:
    id: int
    channel: int
    instruction: str
    success: bool
    data: int
    message: str

    ###############################################################

    def __repr__(self) -> str:
        return json.dumps(asdict(self))

    ###############################################################

    @staticmethod
    def create(response_str: str):
        Response.check_valid(response_str)

        return Response(**json.loads(response_str))

    ###############################################################

    @staticmethod
    def check_valid(response_str: str) -> None:
        if len(response_str) + 1 > MAX_LENGTH:
            raise RuntimeError(
                f"Generate response is too long ({len(response_str)} characters)."
            )

        response_schema_filepath = rc.resource_filename(
            "waterer_backend", str(pt.Path("assets") / "response_schema.json")
        )

        if not pt.Path(response_schema_filepath).is_file():
            raise RuntimeError(f"Missing: {response_schema_filepath}")

        with open(response_schema_filepath, "r") as fh:
            schema = json.load(fh)

        validator = jsonschema.Draft7Validator(schema=schema)

        validator.validate(json.loads(response_str))

    ###############################################################

    def serialize(self) -> str:

        response_str = repr(self)

        self.check_valid(response_str)

        return response_str
