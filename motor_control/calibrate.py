"""
Calibration script using the updated manual_control architecture.
Works over SSH or local terminal.
"""

import select
import json
import time
import threading
import sys
import termios
import tty

from . import manual_control
from .manual_control import initialize_motors
from gpiozero import Button, Device
from gpiozero.pins.rpigpio import RPiGPIOFactory


# ===================== Keyboard =====================


def get_key_nonblocking():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None


# ===================== Homing =====================


def move_to_home(step_delay=0.0000001):
    """
    Home both axes using motor TurnStep for consistent speed with move_to_position.
    Motion stops immediately on endstop trigger.

    :param step_delay: Step delay for motor movement, matches move_to_position speed
    :type step_delay: float
    """
    print("Homing in progress...")

    # ---- X axis (move backward toward X-min) ----
    print("  X axis: moving backward toward endstop...")
    while not manual_control.x_min_pressed.is_set():
        manual_control.Motor2.TurnStep(Dir="backward", steps=20, stepdelay=step_delay)
        time.sleep(0.01)

    print("  X axis: endstop hit, waiting for backoff...")
    # Wait for backoff thread to start
    time.sleep(0.05)

    manual_control.x_min_pressed.clear()
    while manual_control.x_backoff_running.is_set():
        time.sleep(0.1)

    time.sleep(0.2)  # small settle delay
    print("  X axis: homing complete")

    # ---- Y axis (move backward toward Y-min) ----
    print("  Y axis: moving backward toward endstop...")
    while not manual_control.y_min_pressed.is_set():
        manual_control.Motor1.TurnStep(Dir="backward", steps=20, stepdelay=step_delay)
        time.sleep(0.01)

    print("  Y axis: endstop hit, waiting for backoff...")
    # Wait for backoff thread to start
    time.sleep(0.05)

    manual_control.y_min_pressed.clear()
    while manual_control.y_backoff_running.is_set():
        time.sleep(0.1)

    time.sleep(0.2)  # small settle delay
    print("  Y axis: homing complete")

    # Reset counters
    manual_control.x_axis = 0
    manual_control.y_axis = 0

    print("Homing complete")


# ============== Reset State ==============


def reset_manual_state():
    """
    Reset flags and perform homing.
    Must be called AFTER motor_control_loop is running.
    """

    manual_control.is_moving_forward = False
    manual_control.is_moving_backward = False
    manual_control.is_moving_left = False
    manual_control.is_moving_right = False

    manual_control.continuous_forward = False
    manual_control.continuous_backward = False
    manual_control.continuous_left = False
    manual_control.continuous_right = False

    move_to_home()


# ============== Save Calibration ==============


def dump_to_json(x_axis, y_axis, filename="motor_control/calibration_info.json"):
    coords = {"end_position_x": x_axis, "end_position_y": y_axis}

    try:
        with open(filename, "w") as fp:
            json.dump(coords, fp, indent=2)
        print(f"Calibration saved to {filename}")
    except Exception as e:
        print(f"Failed to save calibration: {e}")


# ============== Calibration UI ==============


def calibration_listener():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    print("\nCalibration controls:")
    print("  W = continuous up")
    print("  A = continuous left")
    print("  S = continuous down")
    print("  D = continuous right")
    print("  Y = step up")
    print("  H = step down")
    print("  Z = step left")
    print("  X = step right")
    print("  SPACE = stop all")
    print("  ENTER = save calibration & exit")
    print("  ESC = quit without saving\n")

    try:
        while manual_control.running:
            key = get_key_nonblocking()
            if not key:
                time.sleep(0.01)
                continue

            key = key.lower()

            # Continuous motion
            if key == "w":
                manual_control.continuous_forward = (
                    not manual_control.continuous_forward
                )
                manual_control.continuous_backward = False
                manual_control.continuous_left = False
                manual_control.continuous_right = False

            elif key == "a":
                manual_control.continuous_left = not manual_control.continuous_left
                manual_control.continuous_right = False
                manual_control.continuous_forward = False
                manual_control.continuous_backward = False

            elif key == "s":
                manual_control.continuous_backward = (
                    not manual_control.continuous_backward
                )
                manual_control.continuous_forward = False
                manual_control.continuous_left = False
                manual_control.continuous_right = False

            elif key == "d":
                manual_control.continuous_right = not manual_control.continuous_right
                manual_control.continuous_left = False
                manual_control.continuous_forward = False
                manual_control.continuous_backward = False

            # Single steps
            elif key == "y":
                manual_control.is_moving_forward = True
            elif key == "h":
                manual_control.is_moving_backward = True
            elif key == "z":
                manual_control.is_moving_left = True
            elif key == "x":
                manual_control.is_moving_right = True

            # Stop
            elif key == " ":
                manual_control.continuous_forward = False
                manual_control.continuous_backward = False
                manual_control.continuous_left = False
                manual_control.continuous_right = False

            # Save & exit
            elif key in ("\n", "\r"):
                dump_to_json(manual_control.x_axis, manual_control.y_axis)
                manual_control.running = False

            # Exit without saving
            elif key == "\x1b":
                manual_control.running = False

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


# ============== Entry Point ==============


def start_calibration_control():
    print("Starting calibration in 2 seconds...")
    time.sleep(2)

    # Initialize GPIO and endstops
    Device.pin_factory = RPiGPIOFactory()

    y_min = Button(manual_control.Y_MIN_PIN, pull_up=False)
    x_min = Button(manual_control.X_MIN_PIN, pull_up=True)

    y_min.when_pressed = manual_control.on_y_min_pressed
    y_min.when_released = manual_control.on_y_min_released

    x_min.when_pressed = manual_control.on_x_min_pressed
    x_min.when_released = manual_control.on_x_min_released

    # Initialize motors & GPIO
    Motor1, Motor2, pump1 = initialize_motors()
    manual_control.Motor1 = Motor1
    manual_control.Motor2 = Motor2
    manual_control.pump1 = pump1

    manual_control.running = True

    motor_thread = threading.Thread(
        target=manual_control.motor_control_loop, daemon=True
    )
    motor_thread.start()

    # Give thread time to start
    time.sleep(0.1)

    # Perform homing AFTER motor thread is alive
    reset_manual_state()

    # Enter UI
    calibration_listener()

    # Shutdown
    manual_control.running = False
    Motor1.Stop()
    Motor2.Stop()

    # Clean up GPIO pins
    if hasattr(Motor1, "dir_pin") and Motor1.dir_pin:
        Motor1.dir_pin.close()
    if hasattr(Motor1, "step_pin") and Motor1.step_pin:
        Motor1.step_pin.close()
    if hasattr(Motor1, "enable_pin") and Motor1.enable_pin:
        Motor1.enable_pin.close()

    if hasattr(Motor2, "dir_pin") and Motor2.dir_pin:
        Motor2.dir_pin.close()
    if hasattr(Motor2, "step_pin") and Motor2.step_pin:
        Motor2.step_pin.close()
    if hasattr(Motor2, "enable_pin") and Motor2.enable_pin:
        Motor2.enable_pin.close()

    if y_min:
        y_min.close()
    if x_min:
        x_min.close()

    print("Calibration exited cleanly")


if __name__ == "__main__":
    start_calibration_control()
