# -*- coding: utf-8 -*-

from statistics import mean
from weather import measurements
import csv
import functools
import math
import random


def weather_reading_to_report_line(reading, sep):
    """Generate a report line given a WeatherReading

    Args:
        reading (WeatherReading): A weather reading
        sep (string): seperator

    Returns:
        (string): a line
    """
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
    """Write data to file

    Args:
        data (list[A]): the data to be written to file
        output_file (string): path to output file
        line_processor (function A -> String):
            function to turn a data element into a string
    """
    with open(output_file, 'w') as f:
        for record in data:
            f.write(line_processor(record) + '\n')


def read_csv_file(data_file):
    """Read in a csv file
    Dont use this function for large files

    Args:
        data_file (string): path to file

    Returns:
        (list(dict)): data in the file
    """
    with open(data_file) as f:
        reader = csv.DictReader(f)
        return [rec for rec in reader]


def build_transformer(environment,
                      conditions_updater,
                      temperature_updater,
                      pressure_updater,
                      humidity_updater):
    """Build the transform function that transitions a weather state

    Args:
        environment (simpy.Environment): Containter for the simulation
        conditions_updater (function (double, double, double) ->
                                        measurements.WeatherCondition:
            a function that takes a temperature, current pressure
            and previous pressure to determine the weather condition
        temperature_updater (function (double) -> double):
            a function that takes the day_of_year to determine the temperature
        humidity_updater (function: () -> double):
            a function that takes no parameters and provides the next reading

    Returns:
        (function (WeatherReading) -> WeatherReading):
            given the previous WeatherReading calculate
            the current WeatherReading
    """

    def transformer(weather_reading):
        station = weather_reading.station
        latitude = weather_reading.latitude
        longitude = weather_reading.longitude
        altitude = weather_reading.altitude
        local_time = environment.now
        temperature = temperature_updater(day_of_year=local_time)
        pressure = pressure_updater(temperature, altitude)

        conditions = conditions_updater(temperature,
                                        prev_pressure=weather_reading.pressure,
                                        curr_pressure=pressure)
        humidity = humidity_updater()
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


"""No arg function to get a humidity reading """
humidity_updater = functools.partial(random.uniform, 20, 100)


def temperature(day_of_year, hottest_day, low_temp, high_temp):
    """Calculate the expected temerature for a day, taking
    into account seasonality

    Seasonality is modelled as a cosine wave

    Args:
        day_of_year (int): day of year 0...364
        hottest_day (int): day with hottest average temperature 0...364
        lowest_temp (double): lowest average temperature for a day
        high_temp (double): highest average temperature for a day

    Returns:
        (double): expected temperature for day_of_year
    """
    average_temp = mean([low_temp, high_temp])
    amplitude = average_temp - low_temp
    return amplitude * math.cos((2 * math.pi / 365) *
                                (day_of_year - hottest_day)) + average_temp


def build_temperature_updater(variation, hottest_day, low_temp, high_temp):
    """Return a function to calculate temperature given a day of year
    Allows for the introduction of variation /randomness

    Args:
        variation (function (double) -> double):
            function to introduce randomness if desired
        hottest_day (int): day with hottest average temperature 0...364
        lowest_temp (double): lowest average temperature for a day
        high_temp (double): highest average temperature for a day

    Returns:
        (function (int) -> double):
            function to calculate temperature for day_of_year
    """
    t = functools.partial(temperature,
                          hottest_day=hottest_day,
                          low_temp=low_temp,
                          high_temp=high_temp)

    def temperature_updater(day_of_year):
        return variation(t(day_of_year))

    return temperature_updater


def weather_condition(temperature, prev_pressure, curr_pressure):
    '''Determine weather condition as a function of temperature and pressure change
    With some artistic license inspired by
    http://www.bohlken.net/airpressure2.htm

    Args:
        temperature (double): temperature in celcius
        prev_pressure (double): previous pressure in hpa
        curr_pressure (double): current pressure in hpa
    Returns:
        (measurements.WeatherCondition)
    '''
    delta = curr_pressure - prev_pressure
    down_threshold = -10
    up_threshold = 10

    if down_threshold < delta <= up_threshold:
        return measurements.WeatherCondition.Sunny
    elif delta < down_threshold:
        if temperature < 0:
            return measurements.WeatherCondition.Snow
        else:
            return measurements.WeatherCondition.Rain
    else:
        return measurements.WeatherCondition.Clouds


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
        t = 15  # Degrees celcius
        return (pressure * temperature) / t

    pressure = adjust_for_temperature(to_pressure(altitude),
                                      temperature)
    return to_hpa(pressure)


def to_hpa(pa):
    """Utility function to convert pressure readings from pa to hpa

    Args:
        pa (double): pressure in pa

    Returns:
        hps (double): pressure in hpa
    """
    return pa / 100.0
