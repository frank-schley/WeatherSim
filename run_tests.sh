#!/bin/sh

python -m pytest -s --cov-report term-missing --cov=weather tests/
