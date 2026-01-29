"""
This file is the base for the control of the robot. It allows for manual control of the motors via keyboard input. Read comments
carefully when modifying.
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

# =================== Global Variables ===================

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

# Motor instances
Motor1 = None
Motor2 = None
pump1 = None
servo = None
y_min = None
x_min = None
DeviceFactory = None

# Ensures that variables work across threads
y_min_pressed = threading.Event()
x_min_pressed = threading.Event()
y_backoff_running = threading.Event()
x_backoff_running = threading.Event()

# GPIOs for endstops
Y_MIN_PIN = 6
X_MIN_PIN = 5

#  ----- GPIO Pins for motors and pumps -----

# Motor 1 (Y Axis)
DIR1 = 13  # Direction pin
STEP1 = 19  # Step pin
ENABLE1 = 12  # Enable pin
MODE1 = (16, 17, 20)  # Microstep pins

# Motor 2 (X Axis)
DIR2 = 24  # Direction pin
STEP2 = 18  # Step pin
ENABLE2 = 4  # Enable pin
MODE2 = (21, 22, 27)  # Microstep pins


# Pins for pump one, no ENA is used as highest speed sprays most effective
IN1 = 9  # Direction pin 1
IN2 = 10  # Direction pin 2


# =================== Functions for keyboard input ==================


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
    Terminal-based listener for keyboard control.
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
                if continuous_forward:
                    continuous_backward = False  # stop opposite modes
                    continuous_left = False
                    continuous_right = False

            elif key == "a":
                continuous_left = not continuous_left
                if continuous_left:
                    continuous_right = False  # stop opposite modes
                    continuous_backward = False
                    continuous_forward = False
            elif key == "s":
                continuous_backward = not continuous_backward
                if continuous_backward:
                    continuous_forward = False  # stop opposite modes
                    continuous_left = False
                    continuous_right = False
            elif key == "d":
                continuous_right = not continuous_right
                if continuous_right:
                    continuous_left = False  # stop opposite modes
                    continuous_backward = False
                    continuous_forward = False
            elif key == "r":
                rotate_sponge()
            elif key == "e":
                pump_one_forward(duration=10)
            # These are for one step at a time. Note that this is very slow and we did not use this in calibration
            elif key == "z":
                is_moving_left = True
            elif key == "x":
                is_moving_right = True
            elif key == "y":
                is_moving_forward = True
            elif key == "h":
                is_moving_backward = True

            elif key == " ":  # SPACE
                continuous_forward = False
                continuous_backward = False
                is_moving_forward = False
                is_moving_backward = False

            elif key == "\x1b":  # ESC
                running = False
                break

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# =================== Motor Control Functions ===================

# ------- Basic Step Functions -------
# These functions perform a fixed number of steps in a given direction. The step delay is set so low that
# it is lower than it can actually achieve, to maximize speed. 0.05 from a documentation was slower.


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


def rotate_sponge():
    global servo
    if servo is None:
        print("Servo not initialized")
        return

    servo.min()
    time.sleep(2.5)  # wait for servo to move
    servo.max()
    time.sleep(2.5)  # wait for servo to move
    servo.mid()  # stop signal
    servo.detach()


def pump_one_forward(duration=10):
    """
    Runs motor forward for duration seconds
    """
    global pump1
    pump1.forward()
    time.sleep(duration)
    pump1.stop()


def initialize_motors():
    """
    Initializes motors with pin layout. It is important to not initialize on starting the program, as gpiozero
    seems to have issues if multiple pin factories are used. This function is called after setting the pin factory.
    """
    global IN1, IN2, DIR1, STEP1, ENABLE1, MODE1, DIR2, STEP2, ENABLE2, MODE2

    Motor1 = DRV8825(dir_pin=DIR1, step_pin=STEP1, enable_pin=ENABLE1, mode_pins=MODE1)
    Motor1.SetMicroStep("softward", "1/32step")

    Motor2 = DRV8825(dir_pin=DIR2, step_pin=STEP2, enable_pin=ENABLE2, mode_pins=MODE2)
    Motor2.SetMicroStep("softward", "1/32step")

    pump1 = Motor(forward=IN1, backward=IN2)

    return Motor1, Motor2, pump1


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
        if is_moving_forward or continuous_forward or y_backoff_running.is_set():
            if not y_min_pressed.is_set() or y_backoff_running.is_set():
                step_motor_forward()
                y_axis += 1
            is_moving_forward = False

        if is_moving_backward or continuous_backward:
            if not y_min_pressed.is_set():
                step_motor_backward()
                y_axis -= 1
            else:
                continuous_backward = False
            is_moving_backward = False

        # -------- X AXIS --------
        if is_moving_left or continuous_left:
            step_motor_left()
            x_axis -= 1
            is_moving_left = False

        if is_moving_right or continuous_right or x_backoff_running.is_set():
            if not x_min_pressed.is_set() or x_backoff_running.is_set():
                step_motor_right()
                x_axis += 1
            else:
                continuous_right = False
            is_moving_right = False

        # Small sleep to settle
        time.sleep(0.005)


def move_to_position(calibrated_x, calibrated_y, step_delay=0.0000001):
    """
    Moves device to the calibrated position.
    Steps are always positive; direction is determined by sign of coordinates.
    Stops immediately if endstop is hit while moving backward.
    """
    global Motor1, Motor2

    # Move Y axis
    steps_y = abs(calibrated_y)
    dir_y = "forward" if calibrated_y >= 0 else "backward"
    for _ in range(steps_y):
        # Stop if endstop hit while moving backward
        if dir_y == "backward" and y_min_pressed.is_set():
            break
        Motor1.TurnStep(Dir=dir_y, steps=20, stepdelay=step_delay)

    # Move X axis
    steps_x = abs(calibrated_x)
    dir_x = "forward" if calibrated_x >= 0 else "backward"
    for _ in range(steps_x):
        # Stop if endstop hit while moving backward
        if dir_x == "backward" and x_min_pressed.is_set():
            break
        Motor2.TurnStep(Dir=dir_x, steps=20, stepdelay=step_delay)


# ================== Endstop Handling Functions ===================


def stop_all_motion():
    """
    Stops all motor motion by resetting all movement flags.
    """
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
    """Backs off from the X endstop by moving right (away) for 1 second."""
    global continuous_right
    try:
        end = time.monotonic() + 1
        while time.monotonic() < end:
            continuous_right = True
            time.sleep(0.01)
    finally:
        continuous_right = False
    # Clear flags after backoff completes

    time.sleep(0.1)  # Give it a moment to settle
    x_min_pressed.clear()
    x_backoff_running.clear()


def back_off_y_endstop():
    """Backs off from the Y endstop by moving forward (away) for 1 second."""
    global continuous_forward

    try:
        end = time.monotonic() + 1
        while time.monotonic() < end:
            continuous_forward = True
            time.sleep(0.01)
    finally:
        continuous_forward = False
    # Clear flags after backoff completes
    time.sleep(0.1)  # Give it a moment to settle
    y_min_pressed.clear()
    y_backoff_running.clear()


def on_x_min_pressed():
    """Handles X min endstop press event."""

    if x_backoff_running.is_set():
        return

    x_min_pressed.set()
    stop_all_motion()

    x_backoff_running.set()
    threading.Thread(target=back_off_x_endstop, daemon=True).start()


def on_x_min_released():
    """Handles X min endstop release event. Not really used, but kept for symmetry and possible future use."""
    # Clear flags only after backoff completes (handled in back_off function)


def on_y_min_pressed():
    """Handles Y min endstop press event."""

    if y_backoff_running.is_set():
        return

    y_min_pressed.set()
    stop_all_motion()

    y_backoff_running.set()
    threading.Thread(target=back_off_y_endstop, daemon=True).start()


def on_y_min_released():
    """Handles Y min endstop release event. Not really used, but kept for symmetry and possible future use."""
    # Clear flags only after backoff completes (handled in back_off function)


# =================== Main Function ===================


def start_manual_control():
    """Starts the manual control program. First initializes motors and then starts keyboard listener, after which it cleans up."""
    global running
    global Motor1, Motor2
    global pump1
    global servo, y_min, x_min, DeviceFactory

    # Pin factory for gpiozero, as there were poblems when not set. It looked like there were multiple conflicting pin factories.
    Device.pin_factory = RPiGPIOFactory()

    # Pull up is not the same, this is likely a hardware issue and could easily not work in the future. We did not have time to debug.
    y_min = Button(Y_MIN_PIN, pull_up=False)
    x_min = Button(X_MIN_PIN, pull_up=True)

    try:
        servo = Servo(26)
        servo.detach()  # Important, detach to avoid jitter and power draw
    except Exception as e:
        print(f"Servo init failed: {e}")
        servo = None

    Motor1, Motor2, pump1 = initialize_motors()

    y_min.when_pressed = on_y_min_pressed
    y_min.when_released = on_y_min_released

    x_min.when_pressed = on_x_min_pressed
    x_min.when_released = on_x_min_released

    running = True

    motor_thread = threading.Thread(target=motor_control_loop, daemon=True)
    motor_thread.start()

    keyboard_listener()

    # Cleanup on exit.
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
    x_min.close()

    print("Program exited.")


if __name__ == "__main__":
    start_manual_control()
