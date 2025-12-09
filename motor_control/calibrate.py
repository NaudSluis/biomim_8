import json
import manual
from manual import start_manual_control
from pynput import keyboard
import time

def move_to_home():
    # while home_x != pressed:
    #   left()
    # while home_y != pressed:
    #   down()
    return #this is place holder now to avoid error

def reset_manual_state():
    """Resets the step counters in the 'manual' module before starting."""
    #Move to home first
    print("Moving to home...")
    move_to_home()

    manual.x_axis = 0
    manual.y_axis = 0

    manual.is_moving_forward = False
    manual.is_moving_down = False
    manual.is_moving_right = False
    manual.is_moving_left = False

    print("Moved to home")

def calibrate():
    print("Calibration starting")
    time.sleep(1)
    reset_manual_state()
    print("Press Enter to save position")
    start_manual_control()


if __name__ == "__main__":
    calibrate()
