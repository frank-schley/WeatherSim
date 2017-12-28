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
        pressure = pressure_updater(weather_reading.pressure)
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

def temperature_updater(day_of_year, temperature):
    return temperature


def pressure(temperature, altitude):
    '''Approximates the barometric pressure in hpa
    Sources: - https://en.wikipedia.org/wiki/Barometric_formula
             - https://opentextbc.ca/chemistry
    Args:
        temperature (double): temperature in celcius
        altitude (double): height above sealevel in meters

    Return:
        (double): barometric pressure in hpa
    '''
    t = to_kelvin(celcius=15)
    p = to_pa(hpa=measurements.STANDARD_PRESSURE)
    l = to_kelvin(celcius=measurements.LAPSE_RATE)
    g = measurements.GRAVITATIONAL_CONSTANT
    m = measurements.MOLAR_MASS_EARTH
    h = 11000 # height at bottom of layer in meters
    r = measurements.GAS_CONSTANT
    t = to_kelvin(celcius=15)

    def barometric(altitude):
        return p * math.pow(1 - (l * altitude / t), (g * m) / (r * l))

    def adjust_temperature(pressure, temperature):
        return (barometric(altitude) * temperature) / t

    pressure = adjust_temperature(barometric(altitude),
                                  to_kelvin(temperature))
    return to_hpa(pressure)


def to_pa(hpa):
    return 100 * hpa

def to_hpa(pa):
    return pa / 100.0


def to_kelvin(celcius):
    return celcius + measurements.KELVIN_AT_ZERO_CELCIUS

