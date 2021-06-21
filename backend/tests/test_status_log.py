from waterer_backend.status_log import StatusLog


def trivial_test():

    log = StatusLog(10, 5, 20)

    for p in range(20):
        log.add_sample(p, p)

        print(log.get_values()[0])


trivial_test()
