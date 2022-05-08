# !python3

###############################################################
# Imports
###############################################################

import json
import typing as ty
from abc import ABC, abstractmethod
from collections import deque
from threading import Lock

import numpy as np
from waterer_backend.models import (
    BinaryStatusLogData,
    BinaryStatusLogSettings,
    FloatStatusLogData,
    FloatStatusLogSettings,
)

###############################################################
# Definitions
###############################################################


###############################################################
# Classes
###############################################################


class AbstractStatusLog(ABC):
    @staticmethod
    @abstractmethod
    def from_data(serialized_log: str) -> "AbstractStatusLog":
        ...

    @abstractmethod
    def to_data(self) -> str:
        ...

    @abstractmethod
    def clear(self):
        ...

    @abstractmethod
    def add_sample(self, new_time: float, new_value) -> None:
        ...

    @abstractmethod
    def get_values(
        self, min_time_s: ty.Optional[float] = None
    ) -> ty.Tuple[ty.List[float], ty.List[ty.Any]]:
        ...

    @abstractmethod
    def get_newest_value(self) -> ty.Tuple[ty.Optional[float], ty.Optional[ty.Any]]:
        ...


class FloatStatusLog(AbstractStatusLog):

    """
    Manages a log in which all samples younger than:
    - low_res_switchover_age_s are retained as supplied

    Samples older than this are retained until:
    - low_res_max_age_s

    Provided they are separated from the next oldest sample
    by at least:
    - low_res_interval_s
    """

    def __init__(
        self,
        settings: FloatStatusLogSettings = FloatStatusLogSettings(),
    ) -> None:

        self._lock = Lock()

        with self._lock:

            self._low_res_switchover_age_s = settings.low_res_switchover_age_s
            self._low_res_interval_s = settings.low_res_interval_s
            self._low_res_max_age_s = settings.low_res_max_age_s

        self.clear()

    @staticmethod
    def from_data(
        log_data: FloatStatusLogData,
        settings: FloatStatusLogSettings = FloatStatusLogSettings(),
    ) -> "FloatStatusLog":

        log = FloatStatusLog(settings)

        for index, time in enumerate(log_data.times):
            log.add_sample(time, log_data.values[index])

        return log

    def to_data(self) -> FloatStatusLogData:
        """
        Convert data to json string
        """

        times, values = self.get_values(None)

        return FloatStatusLogData(times=times, values=values)

    def clear(self) -> None:

        with self._lock:

            self._high_res_values: ty.Deque[ty.Optional[float]] = deque()
            self._high_res_times: ty.Deque[float] = deque()

            self._low_res_values: ty.Deque[ty.Optional[float]] = deque()
            self._low_res_times: ty.Deque[float] = deque()

    def add_sample(self, new_time: float, new_value: ty.Optional[float]) -> None:

        with self._lock:

            assert len(self._high_res_times) == 0 or new_time > self._high_res_times[-1]

            self._high_res_times.append(new_time)
            self._high_res_values.append(new_value)

            # Identify older high res values to move to low res

            valid_high_res_index = 0
            for p, log_time in enumerate(self._high_res_times):
                if (new_time - log_time) < self._low_res_switchover_age_s:
                    valid_high_res_index = p
                    break

            for index in range(valid_high_res_index):
                old_time = self._high_res_times.popleft()
                old_value = self._high_res_values.popleft()

                if len(self._low_res_times) == 0:
                    take_sample = True
                elif (old_time - self._low_res_times[-1]) > self._low_res_interval_s:
                    take_sample = True
                else:
                    take_sample = False

                if take_sample:
                    self._low_res_times.append(old_time)
                    self._low_res_values.append(old_value)

            # clean very old samples from low res

            while True:
                if len(self._low_res_times) == 0:
                    break

                if new_time - self._low_res_times[0] > self._low_res_max_age_s:
                    self._low_res_times.popleft()
                    self._low_res_values.popleft()
                else:
                    break

    def get_values(
        self, min_time_s: ty.Optional[float] = None
    ) -> ty.Tuple[ty.List[float], ty.List[ty.Optional[float]]]:
        """
        Returns:
            times,  values
        """

        with self._lock:
            all_times = list(self._low_res_times + self._high_res_times)
            all_values = list(self._low_res_values + self._high_res_values)

            if min_time_s is None:
                return all_times, all_values

            if len(all_times) == 0 or all_times[-1] < min_time_s:
                return [], []

            index = len(all_times) - 1

            while index > 0:
                if all_times[index] <= min_time_s:
                    index += 1
                    break

                index -= 1

            return all_times[index:], all_values[index:]

    def get_newest_value(self) -> ty.Tuple[ty.Optional[float], ty.Optional[float]]:
        """
        Returns:
            times,  values
        """

        with self._lock:
            if len(self._high_res_times) == 0:
                return None, None

            return self._high_res_times[-1], self._high_res_values[-1]


class BinaryStatusLog(AbstractStatusLog):
    def __init__(
        self, settings: BinaryStatusLogSettings = BinaryStatusLogSettings()
    ) -> None:

        self._lock = Lock()

        with self._lock:
            self._max_age_s = settings.max_age_s

        self.clear()

    @staticmethod
    def from_data(
        log_data: BinaryStatusLogData,
        settings: BinaryStatusLogSettings = BinaryStatusLogSettings(),
    ) -> "BinaryStatusLog":

        log = BinaryStatusLog(settings)

        for index, time in enumerate(log_data.times):
            log.add_sample(time, log_data.values[index])

        return log

    def to_data(self) -> BinaryStatusLogData:
        """
        Convert data to json string
        """

        times, values = self.get_values(None)

        return BinaryStatusLogData(times=times, values=values)

    def clear(self) -> None:
        with self._lock:
            self._times: deque[float] = deque()
            self._values: deque[bool] = deque()

    def add_sample(self, new_time: float, new_value: bool) -> None:

        with self._lock:

            if new_value:  # hold on to all true values
                self._times.append(new_time)
                self._values.append(new_value)
            elif len(self._times) <= 2:
                self._times.append(new_time)
                self._values.append(new_value)
            elif self._values[-1] == new_value and self._values[-2] == new_value:
                self._times[-1] = new_time
            else:
                self._times.append(new_time)
                self._values.append(new_value)

            # clean too-old samples

            while True:
                if len(self._times) == 0:
                    break

                if new_time - self._times[0] > self._max_age_s:
                    self._times.popleft()
                    self._values.popleft()
                else:
                    break

    def get_values(
        self, min_time_s: ty.Optional[float] = None
    ) -> ty.Tuple[ty.List[float], ty.List[int]]:
        """
        Returns:
            times,  values
        """
        with self._lock:
            if min_time_s is None:
                return (
                    list(self._times),
                    np.asarray(list(self._values), dtype=np.int_).tolist(),
                )

            if len(self._times) == 0 or self._times[-1] < min_time_s:
                return [], []

            index = len(self._times) - 1

            while index > 0:
                if self._times[index] <= min_time_s:
                    index += 1
                    break

                index -= 1

            return (
                list(self._times)[index:],
                (np.asarray(self._values, dtype=np.int_)[index:]).tolist(),
            )

    def get_newest_value(self) -> ty.Tuple[ty.Optional[float], ty.Optional[int]]:
        """
        Returns:
            time,  value
        """

        with self._lock:

            if len(self._times) == 0:
                return None, None

            return self._times[-1], int(self._values[-1])
