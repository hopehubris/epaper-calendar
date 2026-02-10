#!/bin/bash
# E-Paper Calendar Dashboard - Startup Script
# Uses system Python (which has working GPIO) but still loads project dependencies

cd "$(dirname "$0")"

# Add project path and Waveshare library to Python path
export PYTHONPATH="/home/ashisheth/epaper-calendar:/home/ashisheth/e-Paper/RaspberryPi_JetsonNano/python/lib:$PYTHONPATH"

# Run with system Python 3 (has libgpiod or working GPIO support)
/usr/bin/python3 -m src.main "$@"
