#!/bin/sh

cd /app
pip install -e .
cd test
pip install -r requirements.txt
pytest