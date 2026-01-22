import json
from motor_control import manual_control
from motor_control.calibrate import move_to_home, reset_manual_state
from motor_control.manual_control import initialize_motors, pump_one_forward, pump_two_forward, rotate_sponge, move_to_position
from .DRV8825 import DRV8825
import time
import serial
from datetime import datetime
import threading
from gpiozero import Button, Device
from gpiozero.pins.rpigpio import RPiGPIOFactory


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

def demo():
    """
    Performs one washing cycle and logs to json
    """
    global Motor1, Motor2

    # Initialize GPIO and endstops
    Device.pin_factory = RPiGPIOFactory()
    
    y_min = Button(manual_control.Y_MIN_PIN, pull_up=True)
    x_min = Button(manual_control.X_MIN_PIN, pull_up=True)
    
    y_min.when_pressed = manual_control.on_y_min_pressed
    y_min.when_released = manual_control.on_y_min_released
    
    x_min.when_pressed = manual_control.on_x_min_pressed
    x_min.when_released = manual_control.on_x_min_released

    # Initialize motors
    Motor1, Motor2, pump1, pump2 = initialize_motors()
    manual_control.Motor1 = Motor1
    manual_control.Motor2 = Motor2
    manual_control.pump1 = pump1
    manual_control.pump2 = pump2
    
    manual_control.running = True

    # Start motor control loop thread
    motor_thread = threading.Thread(
        target=manual_control.motor_control_loop,
        daemon=True
    )
    motor_thread.start()
    
    # Give thread time to start
    time.sleep(0.1)

    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:

        move_to_home()

        calibrated_x, calibrated_y = get_calibrated_postion("motor_control/calibration_info.json")
        # calibrated_x_house, _ = get_calibrated_postion("motor_control/calibration_house.json")
        
        print(calibrated_x, calibrated_y)
        if calibrated_x is None or calibrated_y is None:
            print("Calibration data is invalid.")
            return
        

        move_to_position(calibrated_x - 100, calibrated_y)  # Move to spray position
        time.sleep(10)

        pump_one_forward(speed=0.8, duration=10)
        time.sleep(5)

        move_to_position(100, 0)
        time.sleep(2)

        rotate_sponge()
        time.sleep(6)
        
        move_to_position(-100, 0)  # Move back to spray
        time.sleep(5)

        pump_two_forward(speed=0.8, duration=10)
        time.sleep(10)
        
        move_to_home()
        time.sleep(5)

        # move_to_position(calibrated_x_house, 0)  # Move to house position
        

        

    except Exception as e:
        print(f"Error during demo: {e}")
        return
    finally:
        manual_control.running = False
        Motor1.Stop()
        Motor2.Stop()
        
        # Clean up GPIO
        for p in Motor1.mode_pins + Motor2.mode_pins:
            p.close()
        
        Motor1.dir_pin.close()
        Motor1.step_pin.close()
        Motor1.enable_pin.close()
        Motor2.dir_pin.close()
        Motor2.step_pin.close()
        Motor2.enable_pin.close()
        
        y_min.close()
        x_min.close()

    end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    

    try:
        with open("logging.json", "a") as fp:
            json.dump({"start_time": start, "end_time": end}, fp)

    except Exception as e:
        print(f"Error logging data: {e}")
