#!/bin/bash

export PATH=$PATH:/home/group8/bin/arduino-cli

cd /home/group8/biomim_8 || { echo "Failed to change directory"; exit 1; }

echo "Running Pi code..."

#compile arduino code
arduino-cli compile --fqbn arduino:avr:uno arduino_code/wash_loop.ino
if [ $? -ne 0 ]; then
    echo "Arduino code compilation failed"
    exit 1
fi
echo "Arduino code compiled successfully"

# upload arduino code
arduino-cli upload -p /dev/ttyUSB0 --fqbn arduino:avr:uno arduino_code/wash_loop.ino
if [ $? -ne 0 ]; then
    echo "Arduino code upload failed"
    exit 1
fi
echo "Arduino code uploaded successfully"

#Run python script
python3 arduino_control.py
if [ $? -ne 0 ]; then
    echo "Python script execution failed"
    exit 1
fi
echo "Python script executed successfully"


