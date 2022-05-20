# !python3

###############################################################
# Imports
###############################################################

import typing as ty

# from pydantic.dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

###############################################################
# Definitions
###############################################################


###############################################################
# Classes
###############################################################


class ActivationTime(BaseModel):
    hour: int = 8
    minute: int = 0


class SmartPumpSettings(BaseModel):
    dry_humidity_V: float = 3.3
    wet_humidity_V: float = 0
    pump_on_time_s: int = 2
    pump_activation_time: ActivationTime = ActivationTime()
    pump_activation_period_days: int = 1
    feedback_active: bool = False
    feedback_setpoint_pcnt: float = 50
    num_smoothing_samples: float = 10
    name: str = "Unamed pump"

    def __post_init__(self):
        self.validate()

    @property
    def pump_activation_time_as_date(self) -> datetime:
        return datetime(
            1900,
            1,
            1,
            hour=self.pump_activation_time.hour,
            minute=self.pump_activation_time.minute,
        )

    def validate(self):

        if self.wet_humidity_V > self.dry_humidity_V:
            raise ValueError(
                f"Wet humidity: {self.dry_humidity_V} V cannot exceed dry: {self.wet_humidity_V} V"
            )

        if self.pump_on_time_s < 0:
            raise ValueError(
                f"pump_on_time_s: {self.pump_on_time_s} s cannot be negative"
            )

        dt = self.pump_activation_time_as_date  # check construction succeeds

        if self.num_smoothing_samples <= 1:
            raise ValueError(
                f"Number of smoothing samples must be at least 1 (got: {self.num_smoothing_samples})"
            )


class FloatStatusLogData(BaseModel):
    values: ty.List[ty.Optional[float]]
    times: ty.List[float]


class FloatStatusLogSettings(BaseModel):
    low_res_switchover_age_s: float = 3600
    low_res_interval_s: float = 300
    low_res_max_age_s: float = 3600 * 24 * 7


class BinaryStatusLogData(BaseModel):
    values: ty.List[bool]
    times: ty.List[float]


class BinaryStatusLogSettings(BaseModel):
    max_age_s: float = 3600 * 24 * 7


class SmartPumpStatusData(BaseModel):
    rel_humidity_V_log: FloatStatusLogData
    smoothed_rel_humidity_V_log: FloatStatusLogData
    pump_status_log: BinaryStatusLogData


class SmartPumpStatus(BaseModel):
    rel_humidity_V: float
    rel_humidity_pcnt: float
    smoothed_rel_humidity_pcnt: ty.Optional[float]
    pump_running: int
    epoch_time: float


class SmartPumpStatusHistory(BaseModel):
    rel_humidity_V: ty.List[ty.Optional[float]]
    rel_humidity_V_epoch_time: ty.List[float]

    rel_humidity_pcnt: ty.List[ty.Optional[float]]
    rel_humidity_pcnt_epoch_time: ty.List[float]

    smoothed_rel_humidity_pcnt: ty.List[ty.Optional[float]]
    smoothed_rel_humidity_pcnt_epoch_time: ty.List[float]

    pump_running: ty.List[int]
    pump_running_epoch_time: ty.List[float]
