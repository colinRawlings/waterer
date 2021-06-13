#!python3

###############################################################
# Imports
###############################################################

import json
import pathlib as pt
import typing as ty
from dataclasses import asdict, dataclass
from random import randint

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
class Request:
    channel: int
    instruction: str
    data: int
    id: ty.Optional[int] = None

    def __post_init__(self):
        if self.id is None:
            self.id = randint(0, 9999)

    ###############################################################

    def __repr__(self) -> str:
        return json.dumps(asdict(self))

    ###############################################################

    @staticmethod
    def create(request_str: str):
        Request.check_valid(request_str)

        return Request(**json.loads(request_str))

    ###############################################################

    @staticmethod
    def check_valid(request_str: str) -> None:
        if len(request_str) + 1 > MAX_LENGTH:
            raise RuntimeError(
                f"Generate request is too long ({len(request_str)} characters)."
            )

        request_schema_filepath = rc.resource_filename(
            "waterer_backend", str(pt.Path("config") / "request_schema.json")
        )

        if not pt.Path(request_schema_filepath).is_file():
            raise RuntimeError(f"Missing: {request_schema_filepath}")

        with open(request_schema_filepath, "r") as fh:
            schema = json.load(fh)

        validator = jsonschema.Draft7Validator(schema=schema)

        validator.validate(json.loads(request_str))

    ###############################################################

    def serialize(self) -> str:

        request_str = repr(self)

        self.check_valid(request_str)

        return request_str
