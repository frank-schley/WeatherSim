#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simpy


def weather_station(env, msg_queue, num):
    while True:
        record = "Time {t}:I am weatherstation number {num}".format(t=env.now, num=num)
        msg_queue.put(record)
        reporting_interval = 5
        yield env.timeout(reporting_interval)


def screen_sink(env, msg_queue):
    while True:
        record = yield msg_queue.get()
        print(record)


class BroadcastPipe(object):
    """A Broadcast pipe that allows one process to send messages to many.
    Frome the Simpy documentation and hence not tested:
        http://simpy.readthedocs.io/en/latest/examples/process_communication.html

    """

    def __init__(self, env, capacity=simpy.core.Infinity):
        self.env = env
        self.capacity = capacity
        self.pipes = []

    def put(self, value):
        """Broadcast a *value* to all receivers."""
        if not self.pipes:
            raise RuntimeError('There are no output pipes.')
        events = [store.put(value) for store in self.pipes]
        return self.env.all_of(events)  # Condition event for all "events"

    def get_output_conn(self):
        """Get a new output connection for this broadcast pipe.

        The return value is a :class:`~simpy.resources.store.Store`.

        """
        pipe = simpy.Store(self.env, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe


def build_simulation():
    environment = simpy.Environment()
    broadcast_queue = BroadcastPipe(environment)
    environment.process(weather_station(environment, broadcast_queue, 1))
    environment.process(weather_station(environment, broadcast_queue, 2))
    environment.process(screen_sink(environment, broadcast_queue.get_output_conn()))
    return environment


def main():
    environment = build_simulation()
    environment.run(until=16)


if __name__ == '__main__':
    main()


