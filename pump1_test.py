"""
Simple test for pump1 without PWM enable pin.
Runs pump1 forward for a few seconds, then stops.
"""

import time
from gpiozero import Motor
from gpiozero import Device
from gpiozero.pins.rpigpio import RPiGPIOFactory

# Use the same pin factory as your main code
Device.pin_factory = RPiGPIOFactory()

# Pins for pump one (direction pins only)
IN1 = 9   # Forward
IN2 = 10  # Backward

def test_pump1(speed=1.0, duration=2):
    print("Initializing pump1...")
    # Note: omit 'enable' since you're not using it
    pump1 = Motor(forward=IN1, backward=IN2)

    try:
        print(f"Running pump1 forward at full speed for {duration} seconds")
        pump1.forward(speed)  # speed is 0..1, ignored if no PWM
        time.sleep(duration)
    finally:
        print("Stopping pump1")
        pump1.stop()
        pump1.close()

if __name__ == "__main__":
    test_pump1()
    print("Pump1 test complete.")
