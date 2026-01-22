"""
Simple test for pump2 without PWM enable pin.
Runs pump2 forward for a few seconds, then stops.
"""

import time
from gpiozero import Motor
from gpiozero import Device
from gpiozero.pins.rpigpio import RPiGPIOFactory

# Use the same pin factory as your main code
Device.pin_factory = RPiGPIOFactory()

# Pins for pump two (direction pins only)
IN3 = 11  # Forward
IN4 = 23  # Backward

def test_pump2(speed=1.0, duration=2):
    print("Initializing pump2...")
    # Note: omit 'enable' since you're not using it
    pump2 = Motor(forward=IN3, backward=IN4)

    try:
        print(f"Running pump2 forward at full speed for {duration} seconds")
        pump2.forward(speed)  # speed is 0..1, ignored if no PWM
        time.sleep(duration)
    finally:
        print("Stopping pump2")
        pump2.stop()
        pump2.close()

if __name__ == "__main__":
    test_pump2()
    print("Pump2 test complete.")
