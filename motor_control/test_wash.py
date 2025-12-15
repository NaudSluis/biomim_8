import json
from motor_control.calibrate import move_to_home
from .DRV8825 import DRV8825
import time
import serial
from datetime import datetime
# from motor_control.pump import send_arduino_signal
#Initialize motors

Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor1.SetMicroStep('softward', 'fullstep')

def send_arduino_signal(signal):
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    try:
        ser.write(signal.encode('utf-8'))
        time.sleep(0.5)

        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Arduino Response: {line}")
    except Exception as e:
        print(f"Error during serial communication: {e}")
    finally:
        ser.close()

    return

def get_calibrated_postion(json_file: str):
    """
    Retrieves earlier calibrated position
    
    :param json_file: Name of the json file where the calibration data is stored
    :type json_file: str
    """ 
    try:
        with open(json_file, 'r') as fp:
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


def move_to_position(calibrated_x, calibrated_y):
    """
    Moves device to the position determined from earlier calibration
    
    :param calibrated_x: amount of steps on the x-axis
    :param calibrated_y: amount of steps on the y-axis
    """
    try:
        for _ in range(calibrated_y):
            Motor1.TurnStep(Dir='forward', steps=20, stepdelay=0.000001)

        for _ in range(calibrated_x):
            # motor2_stepper1.onestep(direction=stepper.Forward, style=stepper.SINGLE)
            time.sleep(0.01)

    except Exception as e:
        print(f"Error moving to position: {e}")



def demo():
    """
    Performs one washing cycle and logs to json
    """
    start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        move_to_home()
        calibrated_x, calibrated_y = get_calibrated_postion('calibration_info.json')
        print(calibrated_x, calibrated_y)
        if calibrated_x is None or calibrated_y is None:
            print("Calibration data is invalid.")
            return
        move_to_position(calibrated_x - 10, calibrated_y) # Move to spray position
        send_arduino_signal('pump_soap') # Soapy pump in the future
        move_to_position(10, calibrated_y) 
        send_arduino_signal('rotate')
        move_to_position(-10, 0) # Move back to spray 
        send_arduino_signal('pump_water') # Water pump in the future
        move_to_home()

    except Exception as e:
        print(f"Error during demo: {e}")
        return

    end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        with open('calibration_info.json', 'a') as fp:
            json.dump({'start_time': start, 'end_time': end}, fp)

    except Exception as e:
        print(f"Error logging data: {e}")

