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

from motor_control import manual_control


# -------------------- Keyboard --------------------

def get_key_nonblocking():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None


# -------------------- Homing --------------------

def move_to_home():
    """
    Home both axes using the motor_control_loop.
    Motion stops immediately on endstop trigger.
    """
    print("Homing in progress...")

    # ---- Y axis (move DOWN toward Y-min) ----
    manual_control.continuous_backward = True
    while not manual_control.y_min_pressed.is_set():
        time.sleep(0.01)
    manual_control.continuous_backward = False
    print("Y axis homed")

    time.sleep(0.2)  # small settle delay

    # ---- X axis (move LEFT toward X-min) ----
    manual_control.continuous_left = True
    while not manual_control.x_min_pressed.is_set():
        time.sleep(0.01)
    manual_control.continuous_left = False
    print("X axis homed")

    # Reset counters
    manual_control.x_axis = 0
    manual_control.y_axis = 0

    print("Homing complete")


# -------------------- Reset State --------------------

def reset_manual_state():
    """
    Reset flags and perform homing.
    Must be called AFTER motor_control_loop is running.
    """
    print("Resetting manual control state...")

    manual_control.is_moving_forward = False
    manual_control.is_moving_backward = False
    manual_control.is_moving_left = False
    manual_control.is_moving_right = False

    manual_control.continuous_forward = False
    manual_control.continuous_backward = False
    manual_control.continuous_left = False
    manual_control.continuous_right = False

    move_to_home()

    print("Manual state reset complete")


# -------------------- Save Calibration --------------------

def dump_to_json(x_axis, y_axis, filename="motor_control/calibration_info.json"):
    coords = {
        "end_position_x": x_axis,
        "end_position_y": y_axis
    }

    try:
        with open(filename, "w") as fp:
            json.dump(coords, fp, indent=2)
        print(f"Calibration saved to {filename}")
    except Exception as e:
        print(f"Failed to save calibration: {e}")


# -------------------- Calibration UI --------------------

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
                manual_control.continuous_forward = not manual_control.continuous_forward
                manual_control.continuous_backward = False
                manual_control.continuous_left = False
                manual_control.continuous_right = False

            elif key == "a":
                manual_control.continuous_left = not manual_control.continuous_left
                manual_control.continuous_right = False
                manual_control.continuous_forward = False
                manual_control.continuous_backward = False

            elif key == "s":
                manual_control.continuous_backward = not manual_control.continuous_backward
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


# -------------------- Entry Point --------------------

def start_calibration_control():
    print("Starting calibration in 2 seconds...")
    time.sleep(2)

    # Initialize motors & GPIO
    manual_control.start_manual_control = False  # safety if imported elsewhere
    manual_control.running = True

    motor_thread = threading.Thread(
        target=manual_control.motor_control_loop,
        daemon=True
    )
    motor_thread.start()

    # Perform homing AFTER motor thread is alive
    reset_manual_state()

    # Enter UI
    calibration_listener()

    # Shutdown
    manual_control.running = False
    manual_control.Motor1.Stop()
    manual_control.Motor2.Stop()
    print("Calibration exited cleanly")


if __name__ == "__main__":
    start_calibration_control()
