"""This file can be used for calibration. Some functions from manual.py are not used to make sure you cannot
calibrate when just using manual control."""

import json
import manual
from manual import on_release, motor_control_loop
from pynput import keyboard
import time
import threading

def move_to_home():
    """
    Resets to the home position
    """
    try:
        # while home_x != pressed:
        #   left()
        # while home_y != pressed:
        #   down()
        pass  # this is a placeholder now to avoid error
    except Exception as e:
        print(f"Error moving to home position: {e}")
    return


def reset_manual_state():
    """Resets the step counters in the 'manual' module before starting."""
    try:
        print("Moving to home...")
        move_to_home()

        manual.x_axis = 0
        manual.y_axis = 0

        manual.is_moving_forward = False
        manual.is_moving_down = False
        manual.is_moving_right = False
        manual.is_moving_left = False

        print("Moved to home")

    except Exception as e:
        print(f"Error resetting manual state: {e}")


def dump_to_json(x_axis, y_axis):
    """
    Puts saved positions in calibration_info.json
    
    :param x_axis: Number of motor steps on the x-axis
    :param y_axis: Number of motor steps on the y-axis
    """
    coords = {"end position x": x_axis, "end position y": y_axis}

    try:
        with open('calibration_info.json', 'w') as fp:
            json.dump(coords, fp)
    except Exception as e:
        print(f"Error dumping to JSON: {e}")



def on_press_calibration(key):
    """
    Callback function that is executed whenever a key is released. Functions and variables 
    from manual.py are used to ensure uniformity. Still, on_press from manual is not used
    so that you cannot (accidentally) save a calibration position in manual control. 
    """
    try:
        if key == keyboard.Key.esc:
            return False 
        elif key == keyboard.Key.enter:
            # Call the save function using the current global values
            # Since dump_to_json uses the global axis variables, we can pass them.
            dump_to_json(manual.x_axis, manual.y_axis)
            print("Position is saved, exiting calibration mode...")
            time.sleep(1)
            return False

        if key.char == 'w':
            manual.is_moving_forward = True
        elif key.char == 's':
            manual.is_moving_down = True
        elif key.char == 'd':
            manual.is_moving_right = True
        elif key.char == 'a':
            manual.is_moving_left = True

    except AttributeError:
        print("Special key pressed.")

    except Exception as e:
        print(f"Error during key press handling: {e}")


def start_calibration_control():
    try:
        control_thread = threading.Thread(target=motor_control_loop)
        control_thread.daemon = True  # Allows the main program to exit even if this thread is running
        control_thread.start()
        
        # Collect events until released
        with keyboard.Listener(on_press=on_press_calibration, on_release=on_release) as listener:
            print("Listening for key presses... Press 'Esc' to exit.")
            listener.join()
        print("Exiting program.")

    except Exception as e:
        print(f"Error starting calibration control: {e}")


def calibrate():
    """
    Calibration function with terminal interface.
    """
    try:
        print("Calibration starting")
        time.sleep(1)
        reset_manual_state()
        print("Press Enter to save position")
        start_calibration_control()
        
    except Exception as e:
        print(f"Error during calibration: {e}")

