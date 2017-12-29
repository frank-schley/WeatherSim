#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import SafeConfigParser
import functools
import random
import simpy
import weather

from weather import helpers

def get_config():
    """Get the default config

    Returns:
        (SafeConfigParser): the configuration
    """
    parser = SafeConfigParser()
    parser.read('config.ini')
    return parser


def build_sim_with_collector_and_screen_printer(config):
    """Construct the simulation with:
        - a data collector
        - a screen printer that emits records to standard out

    Args:
        config (SafeConfigParser): the configuration

    Returns (Simpy.Environment, DataCollector)
    """
    environment = simpy.Environment()
    broadcast_queue = weather.BroadcastPipe(environment)
    attach_stations(config.get('options', 'stations'),
                    environment,
                    broadcast_queue)
    data_collector = weather.DataCollector(environment,
                                           broadcast_queue.get_output_conn())
    environment.process(screen_printer(environment,
                                       broadcast_queue.get_output_conn()))
    return environment, data_collector


def screen_printer(environment, queue):
    """Prints queued records to standard out

    Args:
        environment (simpy.Environment)
        queue (simpy.Store): the message queue
    """
    while True:
        msg = yield queue.get()
        print(msg)


def attach_stations(stations_file, environment, broadcast_queue):
    """Build and attach the weather stations to the environment

    Args:
        stations_file (string): path to file
        environment(simpy.Environment)
        broadcast_queue (BroadcastPipe): the message queue
    """
    records = helpers.read_csv_file(stations_file)
    for rec in records:
        build_and_attach_station(rec,
                                 environment,
                                 every_day_schedule,
                                 broadcast_queue)


def build_and_attach_station(record, environment, schedule, msg_queue):
    """Build and attach the weather station to the environment

    Args:
        record (dict): a line from the stations_file
        environment(simpy.Environment)
        msg_queue (BroadcastPipe): the message queue
    """

    conditions_updater = helpers.weather_condition
    temperature_updater = helpers.build_temperature_updater(
                                                temperature_variation,
                                                float(record['hottest_day']),
                                                float(record['low_temp']),
                                                float(record['high_temp']))
    pressure_updater = compose(pressure_variation, helpers.pressure)
    humidity_updater = helpers.humidity_updater
    transformer = helpers.build_transformer(environment,
                                            conditions_updater,
                                            temperature_updater,
                                            pressure_updater,
                                            humidity_updater)

    def to_weather_reading(record):
        temperature = temperature_updater(environment.now)
        altitude = float(record['altitude'])
        data = {'station': record['station'],
                'latitude': float(record['latitude']),
                'longitude': float(record['longitude']),
                'altitude': altitude,
                'local_time': environment.now,
                'conditions': weather.WeatherCondition.Sunny,
                'temperature': temperature,
                'pressure': pressure_updater(altitude),
                'humidity': humidity_updater()}
        return weather.WeatherReading(**data)

    reading = to_weather_reading(record)
    weather_state = (transformer, to_weather_reading(record))
    station = weather.weather_station(environment,
                                      weather_state,
                                      schedule,
                                      msg_queue)
    environment.process(station)
    return station


def every_day_schedule():
    """Schedule according to which data is emmitted from the weather station

    Returns:
        (int): the schedule interval
    """
    return 1


def temperature_variation(temperature):
    """Introduce some random variation
    Args:
        temperature (double)

    Returns:
        (double)
    """
    return temperature * random.gauss(mu=1, sigma=0.15)


def pressure_variation(pressure):
    """Introduce some random variation
    Args:
        pressure (double)

    Returns:
        (double)
    """
    return pressure * random.gauss(mu=1, sigma=0.02)


def compose(f, g):
    return lambda x: f(g(x))


def write_to_file(output_file, data):
    """Write the data to file

    Args:
        output_file (string): output file for data
        data (list[WeatherReading]): simulation data
    """
    line_proc = functools.partial(
                    helpers.weather_reading_to_report_line, sep='|')
    helpers.write_data(data, output_file, line_proc)


def main():
    config = get_config()
    simulation, data_collector = build_sim_with_collector_and_screen_printer(
                                                                        config)
    simulation.run(until=config.get('options', 'runtime'))
    write_to_file(config.get('options', 'output_file'), data_collector.data)


if __name__ == '__main__':
    main()
