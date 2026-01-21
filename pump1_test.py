"""
Test L298N motor driver with Raspberry Pi (IN1/IN2, no ENA)
Runs motor forward and backward for 2 seconds each
"""

import time
from gpiozero import DigitalOutputDevice

# Use BCM pin numbering
IN1 = 9
IN2 = 10

# Setup as simple digital outputs
motor_in1 = DigitalOutputDevice(IN1)
motor_in2 = DigitalOutputDevice(IN2)

def forward(duration=2):
    print("Motor forward")
    motor_in1.on()
    motor_in2.off()
    time.sleep(duration)
    motor_in1.off()
    motor_in2.off()

def backward(duration=2):
    print("Motor backward")
    motor_in1.off()
    motor_in2.on()
    time.sleep(duration)
    motor_in1.off()
    motor_in2.off()

if __name__ == "__main__":
    print("Starting pump test (2s forward, 2s backward)")
    forward()
    time.sleep(1)
    backward()
    print("Pump test complete")
