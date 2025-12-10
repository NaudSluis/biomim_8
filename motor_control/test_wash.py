import json
from calibrate import move_to_home
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import time
import serial
from datetime import datetime
#Initialize motors

def rotate_sponge():
    """
    Tells the Arduino to rotate the sponge to clean the window
    """
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2)

    ser.write(b'iets zinnings')
    time.sleep(0.5)

    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()
        if line:
            print(f"Arduino Response: {line}")    
        ser.close()
    return

def get_calibrated_postion(json_file:str):
    """
    Retrieves earlier calibrated position
    
    :param json_file: Name of the json file where the calibration data is stored
    :type json_file: str
    """ 

    with open(json_file, 'r') as fp:
        coords = json.load(fp)
        calibrated_x = int(coords["end position x"])
        calibrated_y = int(coords["end position y"])

    return calibrated_x, calibrated_y

def move_to_calibrated_position(calibrated_x, calibrated_y):
    """
    Moves device to the posistion determined from earlier calibration
    
    :param calibrated_x: amount of steps on the x-axis
    :param calibrated_y: amount of steps on the y-axis
    """

    for _ in range(calibrated_y):
        # motor1_stepper1.onestep(direction=stepper.Forward, style=stepper.SINGLE)
        # motor1_stepper2.onestep(direction=stepper.Forward, style=stepper.SINGLE)
        time.sleep(0.01)

    for _ in range(calibrated_x):
        # motor2_stepper1.onestep(direction=stepper.Forward, style=stepper.SINGLE)
        time.sleep(0.01)



def demo():
    """
    Performs one washing cycle and logs to json
    """

    start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    move_to_home()
    calibrated_x, calibrated_y = get_calibrated_postion('calibration_info.json')
    move_to_calibrated_position(calibrated_x, calibrated_y)
    rotate_sponge()
    move_to_home()

    end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open('calibration_info.json', 'a') as fp:
        json.dump({'start_time': start, 'end_time': end}, fp)
