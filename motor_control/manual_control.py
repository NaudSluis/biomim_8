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
from gpiozero import Motor, Servo

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

servo = None
y_min = None
x_min = None
DeviceFactory = None

# Ensures that variables work across threads
y_min_pressed = threading.Event()
x_min_pressed = threading.Event()
y_backoff_running = threading.Event() 
x_backoff_running = threading.Event()

# Choose GPIOs for endstops
Y_MIN_PIN = 6
X_MIN_PIN = 5

# Pins for pump one
# ENA = 8  # PWM pin (speed)
IN1 = 9  # Direction pin 1
IN2 = 10  # Direction pin 2

# Pins for pump two
IN3 = 11  # Direction pin 1
IN4 = 23   # Direction pin 2
# ENB = 25  # PWM pin (speed)


def rotate_sponge():
    global servo
    if servo is None:
        print("Servo not initialized")
        return

    print("Rotating sponge...")
    servo.min()
    time.sleep(2.5)
    servo.max()
    time.sleep(2.5)
    servo.mid()
    servo.detach()

def pump_one_forward(speed=1.0, duration=10):
    """
    Runs motor forward at given speed (0.0-1.0) for duration in seconds
    """
    global pump1
    pump1.forward(speed)
    time.sleep(duration)
    pump1.stop()

def pump_two_forward(speed=1.0, duration=10):
    """
    Runs motor forward at given speed (0.0-1.0) for duration in seconds
    """
    global pump2
    pump2.forward(speed)
    time.sleep(duration)
    pump2.stop()


# For pin layout, checkout the Waveshare stepper HAT wiki
def initialize_motors():
    """
    Initializes motors with pin layout
    """
    global IN1, IN2, IN3, IN4

    Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
    Motor1.SetMicroStep("softward", "1/32step")

    Motor2 = DRV8825(dir_pin=24, step_pin=18, enable_pin=4, mode_pins=(21, 22, 27))
    Motor2.SetMicroStep("softward", "1/32step")

    pump1 = Motor(forward=IN3, backward=IN4)
    pump2 = Motor(forward=IN1, backward=IN2)

    return Motor1, Motor2, pump1, pump2

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

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    print("Controls:")
    print("  W = toggle continuous up")
    print("  A = toggle continuous left")
    print("  S = toggle continuous down")
    print("  D = toggle continuous right")
    print("  R = Rotate Sponge")
    print("  E = Pump One Forward")
    print("  Q = Pump Two Forward")
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
                rotate_sponge()
            elif key == "e":
                pump_one_forward(speed=1, duration=10)
            elif key == "q":
                pump_two_forward(speed=1, duration=10)
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


def step_motor_forward():
    global Motor1
    Motor1.TurnStep(Dir="forward", steps=20, stepdelay=0.00000001)

def step_motor_backward():
    global Motor1
    Motor1.TurnStep(Dir="backward", steps=20, stepdelay=0.00000001)

def step_motor_right():
    global Motor2
    Motor2.TurnStep(Dir="forward", steps=20, stepdelay=0.00000001)


def step_motor_left():
    global Motor2
    Motor2.TurnStep(Dir="backward", steps=20, stepdelay=0.00000001)


def motor_control_loop():
    global running
    global is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward
    global is_moving_left, is_moving_right
    global continuous_left, continuous_right
    global y_axis, x_axis
    global Motor1, Motor2

    while running:
        # -------- Y AXIS --------
        if is_moving_forward or continuous_forward:
            step_motor_forward()
            y_axis += 1
            is_moving_forward = False  # single step consumed

        if is_moving_backward or continuous_backward:
            # Optional: block by Y min if you want
            if not y_min_pressed.is_set():  # or remove check to always allow backward
                step_motor_backward()
                y_axis -= 1
            is_moving_backward = False

        # -------- X AXIS --------
        if is_moving_left or continuous_left:
            step_motor_left()
            x_axis -= 1
            is_moving_left = False  # single step consumed

        if is_moving_right or continuous_right:
            # Optional: block by X min if needed
            if not x_min_pressed.is_set():  # or remove check to always allow right
                step_motor_right()
                x_axis += 1
            is_moving_right = False

        # Small sleep to prevent CPU hog
        time.sleep(0.005)

def move_to_position(calibrated_x, calibrated_y, step_delay=0.0000001):
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
    dir_x = "backward" if calibrated_x >= 0 else "forward"
    for _ in range(steps_x):
        Motor2.TurnStep(Dir=dir_x, steps=20, stepdelay=step_delay)
        time.sleep(0.01)

def stop_all_motion():
    global is_moving_forward, is_moving_backward
    global is_moving_left, is_moving_right
    global continuous_forward, continuous_backward
    global continuous_left, continuous_right

    is_moving_forward = False
    is_moving_backward = False
    is_moving_left = False
    is_moving_right = False

    continuous_forward = False
    continuous_backward = False
    continuous_left = False
    continuous_right = False

def back_off_x_endstop():
    global continuous_left

    end = time.monotonic() + 1

    while time.monotonic() < end:
        continuous_left = True
        time.sleep(0.01)  # allow motor loop to run

    continuous_left = False
    x_backoff_running.clear()

def back_off_y_endstop():
    global continuous_forward

    try:
        end = time.monotonic() + 0.7
        while time.monotonic() < end:
            continuous_forward = True
            time.sleep(0.01)
    finally:
        continuous_forward = False
        y_backoff_running.clear()



def on_x_min_pressed():
    if x_backoff_running.is_set():
        return  # already backing off

    x_min_pressed.set()
    stop_all_motion()

    x_backoff_running.set()
    threading.Thread(
        target=back_off_x_endstop,
        daemon=True
    ).start()
    
    print("x min endstop hit, all continuous movements stopped.")

def on_x_min_released():
    x_min_pressed.clear()
    print("x min endstop released.")

def on_y_min_pressed():
    if y_backoff_running.is_set():
        return  # already backing off

    y_min_pressed.set()
    stop_all_motion()

    y_backoff_running.set()
    threading.Thread(
        target=back_off_y_endstop,
        daemon=True
    ).start()

    print("y min endstop hit, all continuous movements stopped.")

def on_y_min_released():
    y_min_pressed.clear()
    print("y min endstop released.")

def start_manual_control():
    global running
    global Motor1, Motor2
    global pump1, pump2
    global servo, y_min, x_min, DeviceFactory

    Device.pin_factory = RPiGPIOFactory()

    y_min = Button(Y_MIN_PIN, pull_up=True)
    x_min = Button(X_MIN_PIN, pull_up=True)

    try:
        servo = Servo(26)
        servo.detach()   # VERY IMPORTANT
    except Exception as e:
        print(f"Servo init failed: {e}")
        servo = None

    Motor1, Motor2, pump1, pump2 = initialize_motors()

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
    if servo:
        servo.detach()


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
