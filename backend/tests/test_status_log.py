from waterer_backend.status_log import BinaryStatusLog, FloatStatusLog


def test_get_all_float_log_times():

    low_res_switchover_age_s = 10
    low_res_interval_s = 5
    low_res_max_age_s = 20

    log = FloatStatusLog(
        low_res_switchover_age_s=low_res_switchover_age_s,
        low_res_interval_s=low_res_interval_s,
        low_res_max_age_s=low_res_max_age_s,
    )

    for p in range(2 * low_res_max_age_s):
        log.add_sample(p, p)

        log_times, log_values = log.get_values()
        assert (
            (log_times[-1] - log_times[0]) - low_res_max_age_s
        ) <= low_res_interval_s

    log_times, log_values = log.get_values()
    assert (log_times[1] - log_times[0]) - low_res_interval_s <= 1


def test_get_new_float_log_times():

    low_res_switchover_age_s = 10
    low_res_interval_s = 5
    low_res_max_age_s = 20

    log = FloatStatusLog(
        low_res_switchover_age_s=low_res_switchover_age_s,
        low_res_interval_s=low_res_interval_s,
        low_res_max_age_s=low_res_max_age_s,
    )

    for p in range(2 * low_res_max_age_s):
        log.add_sample(p, p)

    all_log_times, all_log_values = log.get_values()

    target_time = all_log_times[-1] - 5

    new_log_times, new_log_values = log.get_values(target_time)

    assert new_log_times[0] - target_time <= 1


def test_get_all_binary_log_times_all_false():

    log = BinaryStatusLog()

    for p, val in enumerate([False, False, False, False, False]):
        log.add_sample(p, val)
        print(log.get_values()[0])

    all_times, all_values = log.get_values()

    assert len(all_times) == 3


def test_get_all_binary_log_times_one_true():

    log = BinaryStatusLog()

    for p, val in enumerate([False, False, False, False, False, True, False]):
        log.add_sample(p, val)
        print(log.get_values()[0])

    all_times, all_values = log.get_values()

    assert len(all_times) == 5

    new_times, new_values = log.get_values(4.5)
    assert new_times == [5, 6]

    new_times, new_values = log.get_values(20)
    assert new_times == []
