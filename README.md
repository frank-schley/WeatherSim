# WeatherSim

This project demonstrates how to model weather stations and handle their output using a discrete event simulation.

The general idea is that weather stations send readings to a message queue to which interested parties can subscribe.
The current setup has two subscribers, a data collector for batch processing and a 'realtime' process for writing to standard out.
This is a very flexible approach and creates natural seams for testing and extension, even in the face of randomness.


## Prerequisites
- Internet connectivity

    pip3 will pull the project dependencies automatically, but this requires internet access.
- python 3 (tested on python 3.6.3)
- virtualenv
- pip3

## Setup
1. Ensure `setup_virtualenv.sh` has execution permissions
2. Execute: `source setup_virtualenv` This sets up and activates the virualenv. Do this before working on the project.

## Testing
1. Ensure `run_tests.sh` has execution permissions
2. Execute: `./run_tests`
3. A small report will be printed. All Tests should pass with 99% test coverage.

## Running the project
1. Ensure `run_sim.py` has execution permissions
2. Modify `config.ini` to control configuration
2. Execute: `./run_sim.py`

## Design goals
To have fun and explore TDD for building simulations.

