from collections import namedtuple
from enum import Enum


STANDARD_PRESSURE = 1013.25 # Unit: hPa
STANDARD_TEMPERATURE = 15 # Unit: Degrees Celcius
GRAVITATIONAL_CONSTANT = 9.80665 # Unit: m/s2
MOLAR_MASS_EARTH = 0.0289644 # Unit: kg/mol
KELVIN_AT_ZERO_CELCIUS = 273.15 # Unit: Degrees Kelvin
GAS_CONSTANT = 8.3144598 # Unit: J/mol/K
LAPSE_RATE = 0.0098 # Unit: c/m


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
    HeavyClouds = 2
    LightRain = 3
    HeavyRain = 4
