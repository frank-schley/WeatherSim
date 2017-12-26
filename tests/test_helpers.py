# -*- coding: utf-8 -*-

import unittest
import datetime
import shutil
import os

import weather.helpers as helpers
import weather.measurements as measurements

class TestWeatherReadingToReportLine(unittest.TestCase):
    def test_conversion_to_string(self):
        data_points = {'station': 'SYD',
                       'local_time': 1011,
                       'latitude': -33.86,
                       'longitude': 151.12,
                       'conditions': measurements.WeatherCondition.Sunny,
                       'temperature': 19,
                       'pressure': 1014,
                       'humidity': 78}
        reading = measurements.WeatherReading(**data_points)

        expected_line = 'SYD|1011|-33.86|151.12|Sunny|19|1014|78'
        actual_line = helpers.weather_reading_to_report_line(reading, sep='|')
        self.assertEqual(expected_line, actual_line)


class TestWriteData(unittest.TestCase):
    def setUp(self):
        self.output_file = 'tests/test_report.txt'
        try_delete_file(self.output_file)

    def test_no_data_should_result_in_empty_file(self):
        no_records = []
        helpers.write_data(no_records, self.output_file, line_processor=identity)
        self.assertEqual(no_records, read_contents(self.output_file))


def identity(x):
    return x

def read_contents(filename):
    with open(filename) as f:
        return f.readlines()

def delete_file(filename):
    os.remove(filename)


def try_delete_file(filename):
    try:
        delete_file(filename)
    except OSError:
        pass


def try_remove_dir(dir_path):
    '''be careful'''
    try:
        shutil.rmtree(dir_path)
    except OSError:
        pass

