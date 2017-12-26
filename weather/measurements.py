from collections import namedtuple
from enum import Enum

WeatherReading = namedtuple('WeatherReading', ['station',
                                               'latitude',
                                               'longitude',
                                               'local_time',
                                               'conditions',
                                               'temperature',
                                               'pressure',
                                               'humidity'])


class WeatherCondition(Enum):
    Sunny = 0
    Clouds = 1
    HeavyClouds = 2
    LightRain = 3
    HeavyRain = 4
