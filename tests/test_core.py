# -*- coding: utf-8 -*-

from weather import weather_station, WeatherState, DataCollector, BroadcastPipe
import simpy
import unittest
from collections import namedtuple


class WeatherStationTest(unittest.TestCase):

    def setUp(self):
        self.environment = simpy.Environment()
        self.fake_queue = FakeQueue()

    def test_next_weather_should_depend_on_current_weather(self):
        interval_length = 1
        current_temp = 0
        transformer = lambda current_temp: current_temp + 1
        fake_state = WeatherState(transformer=transformer, weather=current_temp)

        self.environment.process(weather_station(
                                        self.environment,
                                        weather_state=fake_state,
                                        schedule=build_fake_schedule(interval=interval_length),
                                        msg_queue=self.fake_queue))

        number_of_readings = 5
        runtime = number_of_readings * interval_length
        self.environment.run(until=runtime)

        expected_weather = list(range(number_of_readings))
        self.assertEqual(expected_weather, self.fake_queue.data)


class FakeQueue(object):
    def __init__(self):
        self.data = []

    def put(self, record):
        self.data.append(record)

    def __len__(self):
        return len(self.data)


def build_fake_schedule(interval):
    def fake_schedule():
        return interval

    return fake_schedule


class CollectorTest(unittest.TestCase):
    def setUp(self):
        self.environment = simpy.Environment()
        self.pipe = BroadcastPipe(self.environment)
        self.collector = DataCollector(self.environment,
                                       msg_queue=self.pipe.get_output_conn())

    def test_new_collector_should_have_no_data(self):
        self.assertEqual([], self.collector.data)

    def test_put_should_track_data(self):
        self.collector.put(value=1)
        self.collector.put(value=2)
        self.assertEqual([1, 2], self.collector.data)

    def test_no_records_should_be_collected_when_no_records_emitted(self):
        no_records = []
        self.check_record_collection(no_records)

    def test_records_should_be_collected_when_records_emitted(self):
        multiple_records = [1, 2, 3, 4, 5]
        self.check_record_collection(multiple_records)

    def check_record_collection(self, records_to_collect):
        self.environment.process(fake_process(self.environment, self.pipe, records_to_collect))
        self.environment.run(until=15)
        self.assertEqual(records_to_collect, self.collector.data)


def fake_process(environment, queue, data):
    for i in data:
        queue.put(i)
        yield environment.timeout(1)


