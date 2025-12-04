#!/bin/bash

cd /home/group8/biomim_8

echo "Running Pi code..."
arduino-cli compile --fqbn arduino:avr:uno arduino_code/wash_loop.ino
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno arduino_code/wash_loop.ino
# Example: Python program
python3 arduino_control.py

