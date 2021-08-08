from waterer_backend.status_log import (
    BinaryStatusLog,
    FloatStatusLog,
    FloatStatusLogSettings,
)


def test_get_all_float_log_times():
    settings = FloatStatusLogSettings(
        low_res_switchover_age_s=10, low_res_interval_s=5, low_res_max_age_s=20
    )
    log = FloatStatusLog(settings)

    for p in range(int(2 * settings.low_res_max_age_s)):
        log.add_sample(p, p)

        log_times, log_values = log.get_values()
        assert (
            (log_times[-1] - log_times[0]) - settings.low_res_max_age_s
        ) <= settings.low_res_interval_s

    log_times, log_values = log.get_values()
    assert (log_times[1] - log_times[0]) - settings.low_res_interval_s <= 1

    # test clear

    log.clear()
    log_times, log_values = log.get_values()
    assert len(log_times) == 0


def test_get_new_float_log_times():

    settings = FloatStatusLogSettings(
        low_res_switchover_age_s=10, low_res_interval_s=5, low_res_max_age_s=20
    )
    log = FloatStatusLog(settings)

    for p in range(int(2 * settings.low_res_max_age_s)):
        log.add_sample(p, p)

    all_log_times, all_log_values = log.get_values()

    target_time = all_log_times[-1] - 5

    new_log_times, new_log_values = log.get_values(target_time)

    assert new_log_times[0] - target_time <= 1

    # test serialize

    log_data = log.to_data()

    new_log = FloatStatusLog.from_data(log_data, settings=settings)

    old_times, old_values = log.get_values()
    new_times, new_values = new_log.get_values()

    assert old_times == new_times
    assert old_values == new_values


def test_get_all_binary_log_times_all_false():

    log = BinaryStatusLog()

    for p, val in enumerate([False, False, False, False, False]):
        log.add_sample(p, val)
        print(log.get_values()[0])

    all_times, all_values = log.get_values()

    assert len(all_times) == 3


def test_clear_all_binary_log_times():

    log = BinaryStatusLog()

    for p, val in enumerate([False, False, False, False, False]):
        log.add_sample(p, val)
        print(log.get_values()[0])

    all_times, all_values = log.get_values()

    assert len(all_times) == 3

    #

    log.clear()

    all_times, all_values = log.get_values()

    assert len(all_times) == 0


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

    # test serialize

    log_data = log.to_data()

    new_log = BinaryStatusLog.from_data(log_data)

    old_times, old_values = log.get_values()
    new_times, new_values = new_log.get_values()

    assert old_times == new_times
    assert old_values == new_values
