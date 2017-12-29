#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import SafeConfigParser
import random
import simpy
import weather

def get_config():
    parser = SafeConfigParser()
    parser.read('config.ini')
    return parser


def build_sim_with_collector(config):
    environment = simpy.Environment()
    broadcast_queue = weather.BroadcastPipe(environment)
    stations = build_stations(config.get('options', 'stations'),
                              environment,
                              broadcast_queue)
    data_collector = weather.DataCollector(environment, broadcast_queue.get_output_conn())
    return environment, data_collector


def build_stations(stations_file, environment, broadcast_queue):
    records = weather.read_csv_file(stations_file)
    stations = [build_station(rec, environment, schedule, broadcast_queue)
                 for rec in records]
    return stations


def variation(number):
    return number * random.gauss(mu=1, sigma=0.05)




def build_station(record, environment,schedule, msg_queue):
    conditions_updater = weather.weather_condition
    temperature_updater = weather.build_temperature_updater(variation,
                                                            float(record['hottest_day']),
                                                            float(record['low_temp']),
                                                            float(record['high_temp']))
    pressure_updater = weather.pressure
    humidity_updater = weather.humidity_updater
    transformer = weather.build_transformer(environment,
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
                'altitude': altitude ,
                'local_time': environment.now,
                'conditions': weather.WeatherCondition.Sunny,
                'temperature': temperature,
                'pressure': pressure_updater(temperature, altitude),
                'humidity': humidity_updater()}
        return weather.WeatherReading(**data)

    reading = to_weather_reading(record)
    weather_state = (transformer, to_weather_reading(record))
    station = weather.weather_station(environment, weather_state, schedule, msg_queue)
    environment.process(station)
    return station



def to_weather_condition(word):
    conditions = {'sunny': weather.WeatherCondition.Sunny,
                  'clouds': weather.WeatherCondition.Clouds,
                  'rain': weather.WeatherCondition.Rain,
                  'snow': weather.WeatherCondition.Snow}
    return conditions[word.lower().strip()]

def schedule():
    return 1


def run(simulation, runtime):
    simulation.run(until=float(runtime))


def main():
    config = get_config()
    simulation, data_collector = build_sim_with_collector(config)
    simulation.run(until=config.get('options', 'runtime'))
    for record in data_collector.data:
        print(record)


if __name__== '__main__':
    main()
