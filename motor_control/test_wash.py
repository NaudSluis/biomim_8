import json
from motor_control.calibrate import move_to_home
from motor_control.manual_control import initialize_motors, pump_one_forward, pump_two_forward, rotate_sponge
from .DRV8825 import DRV8825
import time
import serial
from datetime import datetime


def get_calibrated_postion(json_file: str):
    """
    Retrieves earlier calibrated position

    :param json_file: Name of the json file where the calibration data is stored
    :type json_file: str
    """
    try:
        with open(json_file, "r") as fp:
            coords = json.load(fp)
            calibrated_x = int(coords["end position x"])
            calibrated_y = int(coords["end position y"])

    except FileNotFoundError:
        print(f"Error: {json_file} not found.")
        return None, None

    except json.JSONDecodeError:
        print("Error decoding JSON data.")
        return None, None

    except KeyError as e:
        print(f"Missing key in JSON data: {e}")
        return None, None

    return calibrated_x, calibrated_y



def move_to_position(calibrated_x, calibrated_y, step_delay=0.005):
    """
    Moves device to the calibrated position.
    Steps are always positive; direction is determined by sign of coordinates.
    """
    global Motor1, Motor2
    # Move Y axis
    steps_y = abs(calibrated_y)
    dir_y = "forward" if calibrated_y >= 0 else "backward"
    for _ in range(steps_y):
        Motor1.TurnStep(Dir=dir_y, steps=20, stepdelay=step_delay)

    # Move X axis
    steps_x = abs(calibrated_x)
    dir_x = "forward" if calibrated_x >= 0 else "backward"
    for _ in range(steps_x):
        Motor2.TurnStep(Dir=dir_x, steps=20, stepdelay=step_delay)
        time.sleep(0.01)


def demo():
    """
    Performs one washing cycle and logs to json
    """
    global Motor1, Motor2

    Motor1, Motor2, pump1, pump2, speed_control1, speed_control2 = initialize_motors()

    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:

        move_to_home()

        calibrated_x, calibrated_y = get_calibrated_postion("motor_control/calibration_info.json")
        calibrated_x_house, _ = get_calibrated_postion("motor_control/calibration_house.json")
        
        print(calibrated_x, calibrated_y)
        if calibrated_x is None or calibrated_y is None:
            print("Calibration data is invalid.")
            return
        

        move_to_position(calibrated_x - 10, calibrated_y)  # Move to spray position
        time.sleep(10)

        pump_one_forward(speed=0.8, duration=10)
        time.sleep(5)

        move_to_position(10, 0)
        time.sleep(0)

        rotate_sponge()
        time.sleep(6)
        

        move_to_position(-10, 0)  # Move back to spray
        time.sleep(5)

        pump_two_forward(speed=0.8, duration=10)
        time.sleep(10)
        
        move_to_home()
        time.sleep(15)

        move_to_position(calibrated_x_house, 0)  # Move to house position
        

        

    except Exception as e:
        print(f"Error during demo: {e}")
        return


    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    

    try:
        with open("logging.json", "a") as fp:
            json.dump({"start_time": start, "end_time": end}, fp)

    except Exception as e:
        print(f"Error logging data: {e}")
