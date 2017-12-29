from collections import namedtuple
from enum import Enum


STANDARD_PRESSURE = 1013.25 # Unit: hPa


WeatherReading = namedtuple('WeatherReading', ['station',
                                               'latitude',
                                               'longitude',
                                               'altitude',
                                               'local_time',
                                               'conditions',
                                               'temperature',
                                               'pressure',
                                               'humidity'])


class WeatherCondition(Enum):
    Sunny = 0
    Clouds = 1
    Rain = 2
    Snow = 3
