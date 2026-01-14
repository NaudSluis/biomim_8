"""
This file is the base for the control of the robot.
"""

import sys
import termios
import tty
import time
import serial
import threading
from .DRV8825 import DRV8825
from gpiozero import Button
from gpiozero import Device
from gpiozero.pins.rpigpio import RPiGPIOFactory

is_moving_forward = False  # single step
is_moving_backward = False  # single step
continuous_forward = False  # toggle
continuous_backward = False  # toggle
is_moving_left = False  # single step
is_moving_right = False  # single step
continuous_left = False  # toggle
continuous_right = False  # toggle

y_axis = 0  # Used for calibration counter
x_axis = 0  # Used for calibration counter
running = True

# Ensures that variables work across threads
y_min_pressed = threading.Event()
x_min_pressed = threading.Event()

DeviceFactory = RPiGPIOFactory()

# Choose GPIOs for endstops
Y_MIN_PIN = 6
X_MIN_PIN = 5

y_min = Button(Y_MIN_PIN, pull_up=False)
x_min = Button(X_MIN_PIN, pull_up=False)


def on_x_min_pressed():
    global continuous_forward, continuous_backward
    global continuous_left, continuous_right

    x_min_pressed.set()

    continuous_forward = False
    continuous_backward = False
    continuous_left = False
    continuous_right = False
    print("x min endstop hit, all continuous movements stopped.")

def on_x_min_released():
    x_min_pressed.clear()
    print("x min endstop released.")

def on_y_min_pressed():
    global continuous_forward, continuous_backward
    global continuous_left, continuous_right

    y_min_pressed.set()

    continuous_forward = False
    continuous_backward = False
    continuous_left = False
    continuous_right = False
    print("y min endstop hit, all continuous movements stopped.")

def on_y_min_released():
    y_min_pressed.clear()
    print("y min endstop released.")

# For pin layout, checkout the Waveshare stepper HAT wiki
def initialize_motors():
    """
    Initializes motors with pin layout
    """
    Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
    Motor1.SetMicroStep("softward", "1/32step")

    Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))
    Motor2.SetMicroStep("softward", "1/32step")
    return Motor1, Motor2



def initialize_connection():
    """
    Initializes connection with the Arduino
    """
    try:
        ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}", flush=True)
    return ser


def send_arduino_signal(ser, signal):
    """
    Sends commands to the arduino, which (are supposed to) correspond to the commands in the .ino file

    :param ser: Serial connection initilized by, for example, 'initialize_connection()'
    :param signal: Description
    """
    try:
        # Adds \n so that the arduino code know when to stop reading
        ser.write((signal + "\n").encode("utf-8"))
        time.sleep(0.5)

        while ser.in_waiting > 0:
            line = ser.readline().decode("utf-8").strip()
            if line:
                print(f"Arduino Response: {line}", flush=True)
    except Exception as e:
        print(f"Error during serial communication: {e}", flush=True)

    return


def get_key_nonblocking():
    """
    Get key press from keyboard
    """
    import select

    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None


def keyboard_listener():
    """
    Terminal-based listener for calibration.
    """
    global is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward, running
    global is_moving_left, is_moving_right
    global continuous_left, continuous_right

    ser = initialize_connection()

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    print("Controls:")
    print("  W = toggle continuous up")
    print("  A = toggle continuous left")
    print("  S = toggle continuous down")
    print("  D = toggle continuous right")
    print("  R = Rotate Sponge")
    print("  X = Step right")
    print("  Z = Step left")
    print("  Y = Step up")
    print("  H = Step Down")
    print("  SPACE = stop")
    print("  ESC = quit")

    try:
        while running:
            key = get_key_nonblocking()
            if not key:
                time.sleep(0.01)
                continue

            key = key.lower()

            if key == "w":
                continuous_forward = not continuous_forward
                print(continuous_forward)
                if continuous_forward:
                    continuous_backward = False  # stop opposite mode
                    continuous_left = False
                    continuous_right = False

            elif key == "a":
                continuous_left = not continuous_left
                if continuous_left:
                    continuous_right = False  # stop opposite mode
                    continuous_backward = False
                    continuous_forward = False
            elif key == "s":
                continuous_backward = not continuous_backward
                if continuous_backward:
                    continuous_forward = False  # stop opposite mode
                    continuous_left = False
                    continuous_right = False
            elif key == "d":
                continuous_right = not continuous_right
                if continuous_right:
                    continuous_left = False  # stop opposite mode
                    continuous_backward = False
                    continuous_forward = False
            elif key == "r":
                send_arduino_signal(ser, "rotate")
            elif key == "z":
                is_moving_left = True
            elif key == "x":
                is_moving_right = True
            elif key == "y":
                is_moving_forward = True
            elif key == "h":
                is_moving_backward = True

            elif key == " ":
                continuous_forward = False
                continuous_backward = False
                is_moving_forward = False
                is_moving_backward = False

            elif key == "\x1b":  # ESC
                running = False
                break

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        ser.close()


def step_motor_forward():
    Motor1.TurnStep(Dir="forward", steps=20, stepdelay=0.00000001)

def step_motor_backward():
    Motor1.TurnStep(Dir="backward", steps=20, stepdelay=0.00000001)


def step_motor_right():
    Motor2.TurnStep(Dir="forward", steps=20, stepdelay=0.00000001)


def step_motor_left():
    Motor2.TurnStep(Dir="backward", steps=20, stepdelay=0.00000001)


def motor_control_loop():
    global running, is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward
    global is_moving_left, is_moving_right
    global continuous_left, continuous_right
    global y_axis, x_axis

    while running:
        # -------- Y AXIS --------
        if is_moving_forward:
            if not y_min_pressed.is_set():
                step_motor_forward()
                y_axis += 1
            is_moving_forward = False

        elif continuous_forward:
            if not y_min_pressed.is_set():
                step_motor_forward()
                y_axis += 1
            else:
                time.sleep(0.01)

        elif is_moving_backward:
            step_motor_backward()
            y_axis -= 1
            is_moving_backward = False

        elif continuous_backward:
            step_motor_backward()
            y_axis -= 1

        # -------- X AXIS --------
        elif is_moving_left:
            if not x_min_pressed.is_set():
                step_motor_left()
                x_axis -= 1
            is_moving_left = False

        elif continuous_left:
            if not x_min_pressed.is_set():
                step_motor_left()
                x_axis -= 1
            else:
                time.sleep(0.01)

        elif is_moving_right:
            step_motor_right()
            x_axis += 1
            is_moving_right = False

        elif continuous_right:
            step_motor_right()
            x_axis += 1

        else:
            time.sleep(0.01)



def start_manual_control():
    global running
    global Motor1, Motor2

    Motor1, Motor2 = initialize_motors()

    y_min.when_pressed = on_y_min_pressed
    y_min.when_released = on_y_min_released

    x_min.when_pressed = on_x_min_pressed
    x_min.when_released = on_x_min_released

    running = True

    motor_thread = threading.Thread(target=motor_control_loop, daemon=True)
    motor_thread.start()

    keyboard_listener()

    running = False
    Motor1.Stop()
    Motor2.Stop()

    for p in Motor1.mode_pins + Motor2.mode_pins:
        p.close()

    Motor1.dir_pin.close()
    Motor1.step_pin.close()
    Motor1.enable_pin.close()
    Motor2.dir_pin.close()
    Motor2.step_pin.close()
    Motor2.enable_pin.close()

    y_min.close()

    print("Program exited.")


if __name__ == "__main__":
    start_manual_control()
