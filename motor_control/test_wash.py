import json
import sys
from motor_control import manual_control
from motor_control.calibrate import move_to_home, reset_manual_state
from motor_control.manual_control import (
    initialize_motors,
    pump_one_forward,
    pump_two_forward,
    rotate_sponge,
    move_to_position,
)
from .DRV8825 import DRV8825
import time
import serial
from datetime import datetime
import threading
from gpiozero import Button, Device
from gpiozero.pins.rpigpio import RPiGPIOFactory

# ===================== Calibration Data Retrieval =====================


def get_calibrated_postion(json_file: str):
    """
    Retrieves earlier calibrated position

    :param json_file: Name of the json file where the calibration data is stored
    :type json_file: str
    """
    try:
        with open(json_file, "r") as fp:
            coords = json.load(fp)
            calibrated_x = int(coords["end_position_x"])
            calibrated_y = int(coords["end_position_y"])

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


# ===================== Wash Cycle =====================


def demo():
    """
    Performs one washing cycle and logs to json
    """

    # Initialize GPIO factory FIRST, before any motor initialization
    Device.pin_factory = RPiGPIOFactory()

    # Initialize motors
    Motor1, Motor2, pump1 = initialize_motors()
    manual_control.Motor1 = Motor1
    manual_control.Motor2 = Motor2
    manual_control.pump1 = pump1

    # Initialize servo
    try:
        manual_control.servo = manual_control.Servo(26)
        manual_control.servo.detach()  # Important to avoid jitter
    except Exception as e:
        print(f"Servo init failed: {e}")
        manual_control.servo = None

    # Initialize endstops
    y_min = Button(manual_control.Y_MIN_PIN, pull_up=True)
    x_min = Button(manual_control.X_MIN_PIN, pull_up=True)

    y_min.when_pressed = manual_control.on_y_min_pressed
    y_min.when_released = manual_control.on_y_min_released

    x_min.when_pressed = manual_control.on_x_min_pressed
    x_min.when_released = manual_control.on_x_min_released

    manual_control.running = True

    # Start motor control loop thread
    motor_thread = threading.Thread(
        target=manual_control.motor_control_loop, daemon=True
    )
    motor_thread.start()

    # Give thread time to start
    time.sleep(0.1)

    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:

        move_to_home()

        calibrated_x, calibrated_y = get_calibrated_postion(
            "motor_control/calibration_info.json"
        )
        # calibrated_x_house, _ = get_calibrated_postion("motor_control/calibration_house.json")

        if calibrated_x is None or calibrated_y is None:
            print("Calibration data is invalid.")
            return

        move_to_position(0, calibrated_y)  # Move to spray position

        pump_one_forward(duration=10)

        move_to_position(calibrated_x, 0)

        rotate_sponge()

        move_to_position(-calibrated_x, 0)  # Move back to spray

        pump_one_forward(duration=10)

        move_to_home()

        # move_to_position(calibrated_x_house, 0)  # Move to house position

    except Exception as e:
        print(f"Error during demo: {e}")
    finally:
        manual_control.running = False

        # Safely stop motors if they were initialized
        try:
            if "Motor1" in locals():
                Motor1.Stop()
            if "Motor2" in locals():
                Motor2.Stop()
        except Exception as e:
            print(f"Error stopping motors: {e}")

        # Clean up GPIO pins
        try:
            if "Motor1" in locals() and hasattr(Motor1, "dir_pin") and Motor1.dir_pin:
                Motor1.dir_pin.close()
            if "Motor1" in locals() and hasattr(Motor1, "step_pin") and Motor1.step_pin:
                Motor1.step_pin.close()
            if (
                "Motor1" in locals()
                and hasattr(Motor1, "enable_pin")
                and Motor1.enable_pin
            ):
                Motor1.enable_pin.close()

            if "Motor2" in locals() and hasattr(Motor2, "dir_pin") and Motor2.dir_pin:
                Motor2.dir_pin.close()
            if "Motor2" in locals() and hasattr(Motor2, "step_pin") and Motor2.step_pin:
                Motor2.step_pin.close()
            if (
                "Motor2" in locals()
                and hasattr(Motor2, "enable_pin")
                and Motor2.enable_pin
            ):
                Motor2.enable_pin.close()

            if y_min:
                y_min.close()
            if x_min:
                x_min.close()
        except Exception as e:
            print(f"Error cleaning up GPIO: {e}")

    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with open("logging.json", "a") as fp:
            json.dump({"start_time": start, "end_time": end}, fp)

    except Exception as e:
        print(f"Error logging data: {e}")

    # Exit the entire program
    sys.exit(0)
