# -*- coding: utf-8 -*-

import csv
import functools
import random
import math
from weather import measurements

def weather_reading_to_report_line(reading, sep):
    data = [reading.station,
            str(reading.local_time),
            str(reading.latitude),
            str(reading.longitude),
            str(reading.altitude),
            reading.conditions.name,
            str(reading.temperature),
            str(reading.pressure),
            str(reading.humidity)]
    return sep.join(data)


def write_data(data, output_file, line_processor):
    with open(output_file, 'w') as f:
        for record in data:
            f.write(line_processor(record) + '\n')


def read_csv_file(data_file):
    with open(data_file) as f:
        reader = csv.DictReader(f)
        return [rec for rec in reader]


def build_transformer(conditions_updater,
                      temperature_updater,
                      pressure_updater,
                      humidity_updater):


    def transformer(weather_reading):
        station = weather_reading.station
        latitude = weather_reading.latitude
        longitude = weather_reading.longitude
        altitude = weather_reading.altitude
        local_time = weather_reading.local_time
        conditions = conditions_updater(weather_reading.conditions)
        temperature = temperature_updater(weather_reading.temperature)
        pressure = pressure_updater(temperature, altitude)
        humidity = humidity_updater(weather_reading.humidity)

        return measurements.WeatherReading(station,
                                           latitude,
                                           longitude,
                                           altitude,
                                           local_time,
                                           conditions,
                                           temperature,
                                           pressure,
                                           humidity)
    return transformer




humidity_updater = functools.partial(random.uniform,20,100)


def next_temperature(day_of_year, temperature, variation, season):
    '''Calculate the next temperature
    Args:
        day_of_year (integer): first of jan is day 1
        temperature (double): current temperature
        variation (function): introduces potential randomness
        season (function: int -> double): returns coefficent for seasonality
    Returns:
        (double): next temperature
    '''
    return variation() * season(day_of_year) * temperature


def pressure(temperature, altitude):
    '''Approximates the barometric pressure in hpa
    Sources: - A Quick Derivation relating altitude to air pressure
               from ortland State Aerospace Society, Version 1.03, 12/22/2004
             - https://opentextbc.ca/chemistry
    Args:
        temperature (double): temperature in celcius
        altitude (double): height above sealevel in meters

    Returns:
        (double): barometric pressure in hpa
    '''

    def to_pressure(altitude):
        return 100 * ((44331.514 - altitude) / 11880.516) ** (1 / 0.1902632)

    def adjust_for_temperature(pressure, temperature):
        t = 15 # Degrees celcius
        return (pressure * temperature) / t

    pressure = adjust_for_temperature(to_pressure(altitude),
                                      temperature)
    return to_hpa(pressure)


def to_hpa(pa):
    return pa / 100.0

