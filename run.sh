#!/bin/bash

cd /home/group8/biomim_8

echo "Running Pi code..."
arduino-cli compile --fqbn arduino:avr:uno arduino_code/
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno arduino_code/
# Example: Python program
python3 main.py

# Example: Compile and flash Arduino (if needed)
# arduino-cli compile --fqbn arduino:avr:uno arduino_code/
# arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno arduino_code/
