# -*- coding: utf-8 -*-

import simpy
from collections import namedtuple


WeatherState = namedtuple('WeatherState', ['transformer', 'weather'])


def weather_station(environment, weather_state, schedule, msg_queue):
    """A weather station represented by a generator function

    Args:
        environment (simpy.Environment): container for the simulation
        weather_state ((transformer), (WeatherReading)): Current state of the weather station
        schedule (function: -> double): generates the intervals at which the station emits data
    """

    while True:
        msg_queue.put(weather_state[1])
        weather_state = update_weather(weather_state)
        yield environment.timeout(schedule())


def update_weather(weather_state):
    """Generate next weather state

    Args:
        weather_state ((transformer), (WeatherReading)): Current state of the weather station

    Returns:
        (transformer, WeatherReading): Next state of the weather station

    """
    transformer, current_weather = weather_state
    next_weather = transformer(current_weather)
    return WeatherState(transformer, next_weather)


class BroadcastPipe(object):
    """A Broadcast pipe that allows one process to send messages to many.
    Frome the Simpy documentation and hence not tested directly:
        http://simpy.readthedocs.io/en/latest/examples/process_communication.html
    """

    def __init__(self, environment, capacity=simpy.core.Infinity):
        self.environment = environment
        self.capacity = capacity
        self.pipes = []

    def put(self, value):
        """Broadcast a *value* to all receivers."""
        if not self.pipes:
            raise RuntimeError('There are no output pipes.')
        events = [store.put(value) for store in self.pipes]
        return self.environment.all_of(events)  # Condition event for all "events"

    def get_output_conn(self):
        """Get a new output connection for this broadcast pipe.

        Returns:
            (simpy.resources.store.Store): the queue

        """
        pipe = simpy.Store(self.environment, capacity=self.capacity)
        self.pipes.append(pipe)
        return pipe


class DataCollector(object):
    """Collect records during the simulation from the msg_queue
    and make them available after the run
    """
    def __init__(self, environment, msg_queue):
        self.queue = msg_queue
        self._data = []
        environment.process(self.run())

    @property
    def data(self):
        return self._data

    def put(self, value):
        self._data.append(value)

    def run(self):
        while True:
            msg = yield self.queue.get()
            self.put(msg)


