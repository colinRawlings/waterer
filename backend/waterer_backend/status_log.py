# !python3

###############################################################
# Imports
###############################################################

import typing as ty
from abc import ABC, abstractmethod
from collections import deque
from threading import Lock

###############################################################
# Classes
###############################################################


class AbstractStatusLog(ABC):
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
        low_res_switchover_age_s: float = 3600,
        low_res_interval_s: float = 300,
        low_res_max_age_s: float = 3600 * 24 * 7,
    ) -> None:

        self._lock = Lock()

        with self._lock:

            self._low_res_switchover_age_s = low_res_switchover_age_s
            self._low_res_interval_s = low_res_interval_s
            self._low_res_max_age_s = low_res_max_age_s

        self.clear()

    def clear(self) -> None:

        with self._lock:

            self._high_res_values = deque()
            self._high_res_times = deque()

            self._low_res_values = deque()
            self._low_res_times = deque()

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
    ) -> ty.Tuple[ty.List[float], ty.List[float]]:
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
    def __init__(self, max_age_s: float = 3600 * 24 * 7) -> None:

        self._lock = Lock()

        with self._lock:
            self._max_age_s = max_age_s

        self.clear()

    def clear(self) -> None:
        with self._lock:
            self._times: deque[float] = deque()
            self._values: deque[bool] = deque()

    def add_sample(self, new_time: float, new_value: bool) -> None:

        with self._lock:

            if new_value:  # hold on to all true values
                self._times.append(new_time)
                self._values.append(new_value)
            if len(self._times) <= 2:
                self._times.append(new_time)
                self._values.append(new_value)
            elif self._values[-1] != new_value:
                self._times.append(new_time)
                self._values.append(new_value)
            else:
                self._times[-1] = new_time

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
    ) -> ty.Tuple[ty.List[float], ty.List[bool]]:
        """
        Returns:
            times,  values
        """
        with self._lock:
            if min_time_s is None:
                return list(self._times), list(self._values)

            if len(self._times) == 0 or self._times[-1] < min_time_s:
                return [], []

            index = len(self._times) - 1

            while index > 0:
                if self._times[index] <= min_time_s:
                    index += 1
                    break

                index -= 1

            return list(self._times)[index:], list(self._values)[index:]

    def get_newest_value(self) -> ty.Tuple[ty.Optional[float], ty.Optional[bool]]:
        """
        Returns:
            time,  value
        """

        with self._lock:

            if len(self._times) == 0:
                return None, None

            return self._times[-1], self._values[-1]
