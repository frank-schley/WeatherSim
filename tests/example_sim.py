#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simpy


def weather_station(env, msg_queue):
    while True:
        record = "Time {t}:I am the weatherstation".format(t=env.now)
        msg_queue.put(record)
        reporting_interval = 5
        yield env.timeout(reporting_interval)


def sink(env, msg_queue):
    while True:
        record = yield msg_queue.get()
        print(record)



def build_simulation():
    environment = simpy.Environment()
    msg_queue = simpy.Store(environment)
    environment.process(weather_station(environment, msg_queue))
    environment.process(sink(environment, msg_queue))
    return environment


def main():
    environment = build_simulation()
    environment.run(until=16)


if __name__ == '__main__':
    main()


