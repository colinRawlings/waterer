# !python3

###############################################################
# Imports
###############################################################

import typing as ty

# import numpy as np
from collections import deque

###############################################################
# Classes
###############################################################


class StatusLog:

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

        self._low_res_switchover_age_s = low_res_switchover_age_s
        self._low_res_interval_s = low_res_interval_s
        self._low_res_max_age_s = low_res_max_age_s

        self._high_res_values = deque()
        self._high_res_times = deque()

        self._low_res_values = deque()
        self._low_res_times = deque()

    def add_sample(self, new_time: float, new_value: float):

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

            if self._low_res_times[0] - new_time > self._low_res_max_age_s:
                self._low_res_times.popleft()
                self._low_res_values.popleft()

    def get_values(
        self, max_age: ty.Optional[float] = None
    ) -> ty.Tuple[ty.Iterable[float], ty.Iterable[float]]:
        assert max_age is None

        return (
            self._low_res_times + self._high_res_times,
            self._low_res_values + self._high_res_values,
        )
