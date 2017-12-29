# -*- coding: utf-8 -*-

import unittest
import datetime
import shutil
import os
import csv

import weather.helpers as helpers
import weather.measurements as measurements

class TestWeatherReadingToReportLine(unittest.TestCase):
    def test_conversion_to_string(self):
        data_points = {'station': 'SYD',
                       'local_time': 1011,
                       'latitude': -33.86,
                       'longitude': 151.12,
                       'altitude': 10,
                       'conditions': measurements.WeatherCondition.Sunny,
                       'temperature': 19,
                       'pressure': 1014,
                       'humidity': 78}
        reading = measurements.WeatherReading(**data_points)

        expected_line = 'SYD|1011|-33.86|151.12|10|Sunny|19|1014|78'
        actual_line = helpers.weather_reading_to_report_line(reading, sep='|')
        self.assertEqual(expected_line, actual_line)


class TestWriteData(unittest.TestCase):
    def setUp(self):
        self.output_file = 'tests/scratch_dir/test_report.txt'
        try_delete_file(self.output_file)

    def test_no_data_should_result_in_empty_file(self):
        no_data = []
        self.write_and_check_data(no_data, no_data, double_chars)

    def test_data_should_be_written_to_file_using_the_line_processor(self):
        records = ['a', 'b']
        expected_data = [double_chars(c) for c in records]
        self.write_and_check_data(records, expected_data, double_chars)


    def write_and_check_data(self, data, expected_data, line_processor):
        helpers.write_data(data, self.output_file, line_processor)
        self.assertEqual(expected_data, read_contents(self.output_file))


class TestReadCSVFile(unittest.TestCase):
    def setUp(self):
        self.test_file = 'tests/scratch_dir/csv_test.csv'
        self.fieldnames = ['first_col', 'second_col']
        try_delete_file(self.test_file)

    def test_reading_empty_file_should_return_empty_list(self):
        test_data = []
        self.to_file(test_data, self.fieldnames, self.test_file)
        actual_records = helpers.read_csv_file(self.test_file)
        self.assertEqual(test_data, actual_records)


    def test_reading_multiple_lines_should_return_records(self):
        test_data = [{'first_col': 'a', 'second_col': 'b'},
                     {'first_col': 'b', 'second_col': 'd'}]
        self.to_file(test_data, self.fieldnames, self.test_file)
        actual_records = helpers.read_csv_file(self.test_file)
        self.assertEqual(test_data, actual_records)

    def to_file(self, records, fieldnames, filename):
        with open(filename, 'w') as f:
            writer = csv.DictWriter(f, fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow(record)

class TestWeatherTransformation(unittest.TestCase):
    def test_should_not_transform_under_identity_function(self):
        def pressure_fake(temp, alt):
            return 1000

        def weather_condition_fake(temperature, prev_pressure, curr_pressure):
            return measurements.WeatherCondition.Sunny

        def temperature_fake(day_of_year):
            return 1

        def humidity_fake():
            return 1

        class FakeEnv(object):
            @property
            def now(self):
                return 10

        base_weather = measurements.WeatherReading(station='syd',
                                                   latitude=1,
                                                   longitude=1,
                                                   altitude=1,
                                                   local_time=10,
                                                   conditions=measurements.WeatherCondition.Sunny,
                                                   temperature=1,
                                                   pressure=1000,
                                                   humidity=1)

        transformer = helpers.build_transformer(environment=FakeEnv(),
                                                conditions_updater=weather_condition_fake,
                                                temperature_updater=temperature_fake,
                                                pressure_updater=pressure_fake,
                                                humidity_updater=humidity_fake)
        self.assertEqual(base_weather, transformer(base_weather))


class TestTemperature(unittest.TestCase):

    def test_constant_temperature(self):
        day_of_year = 0
        hottest_day = 0
        low_temp = 0
        high_temp = 0

        self.assertEqual(0, helpers.temperature(day_of_year, hottest_day, low_temp, high_temp))

    def test_hottest_day(self):
        day_of_year = 100
        hottest_day = 100
        low_temp = 0
        high_temp = 10
        self.assertAlmostEqual(high_temp,
                               helpers.temperature(day_of_year, hottest_day, low_temp, high_temp),
                               delta=0.01)

    def test_coldest_day(self):
        day_of_year = 182
        hottest_day = 0
        low_temp = 0
        high_temp = 100
        self.assertAlmostEqual(low_temp,
                               helpers.temperature(day_of_year, hottest_day, low_temp, high_temp),
                               delta=0.01)


class TestTemperatureBuilder(unittest.TestCase):
    def test_basic_usage(self):


        hottest_day = 0
        low_temp = 0
        high_temp = 100
        temp_update = helpers.build_temperature_updater(identity,
                                                        hottest_day,
                                                        low_temp,
                                                        high_temp)
        self.assertAlmostEqual(high_temp,
                               temp_update(day_of_year=hottest_day),
                               delta=0.01)


class TestWeatherCondition(unittest.TestCase):
    def test_no_pressure_should_should_be_sunny(self):
        temperature = 10
        current_pressure = 1000
        previous_pressure = 1000
        self.assertEqual(measurements.WeatherCondition.Sunny,
                         helpers.weather_condition(temperature,
                                                   previous_pressure,
                                                   current_pressure))

    def test_negative_change_should_be_rain_or_snow(self):
        not_freezing = 0
        current_pressure = 1000
        previous_pressure = 1011
        self.assertEqual(measurements.WeatherCondition.Rain,
                         helpers.weather_condition(not_freezing,
                                                   previous_pressure,
                                                   current_pressure))
        cold = -10
        current_pressure = 1000
        previous_pressure = 1011
        self.assertEqual(measurements.WeatherCondition.Snow,
                         helpers.weather_condition(cold,
                                                   previous_pressure,
                                                   current_pressure))

    def test_positive_change_chould_be_clouds(self):
        cold = -10
        current_pressure = 1020
        previous_pressure = 1000
        self.assertEqual(measurements.WeatherCondition.Clouds,
                         helpers.weather_condition(cold,
                                                   previous_pressure,
                                                   current_pressure))





class TestPressureCalculation(unittest.TestCase):
    def test_standard_values(self):
        # Test values taken from https://en.wikipedia.org/wiki/Barometric_formula
        self.assertAlmostEqual(measurements.STANDARD_PRESSURE,
                                helpers.pressure(temperature=15, altitude=0),
                                delta=0.005)

        self.assertAlmostEqual(226.321,
                                helpers.pressure(temperature=15, altitude=11000),
                                delta=0.05)


def identity(x):
    return x


def double_chars(x):
    return str(2 * x)


def years(n):
    return n * 365


def read_contents(filename):
    with open(filename) as f:
        return f.read().splitlines()


def delete_file(filename):
    os.remove(filename)


def try_delete_file(filename):
    try:
        delete_file(filename)
    except OSError:
        pass
