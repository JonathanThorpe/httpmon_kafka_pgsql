#!/bin/sh
#This script is intended to run inside a container for the purposes of setting up test dependencies and running them
cd /app
pip install -e .
cd test
pip install -r requirements.txt
pytest