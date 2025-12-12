"""
Calibration script using the updated manual control setup.
No pynput dependency; works over SSH or local terminal.
"""

import json
import time
import threading
import sys
import termios
import tty
from motor_control import manual_control


def get_key_nonblocking():
    import select
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None


def move_to_home():
    """
    Resets to the home position (placeholder)
    """
    try:
        # Implement actual homing if necessary
        pass
    except Exception as e:
        print(f"Error moving to home position: {e}")


def reset_manual_state():
    """Reset motor step counters and flags in manual_control."""
    try:
        print("Moving to home...")
        move_to_home()

        manual_control.x_axis = 0
        manual_control.y_axis = 0

        manual_control.is_moving_forward = False
        manual_control.is_moving_backward = False
        manual_control.continuous_forward = False
        manual_control.continuous_backward = False

        print("Moved to home")

    except Exception as e:
        print(f"Error resetting manual state: {e}")


def dump_to_json(x_axis, y_axis):
    """Save calibration positions to JSON."""
    coords = {"end position x": x_axis, "end position y": y_axis}

    try:
        with open('calibration_info.json', 'w') as fp:
            json.dump(coords, fp)
    except Exception as e:
        print(f"Error dumping to JSON: {e}")


def calibration_listener():
    """
    Terminal-based listener for calibration.
    Supports W/S single step, E/D continuous, SPACE stop, Enter = save, ESC = exit.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        print("Calibration started. Controls:")
        print("  W = single step forward")
        print("  S = single step backward")
        print("  E = toggle continuous forward")
        print("  D = toggle continuous backward")
        print("  SPACE = stop")
        print("  ENTER = save position")
        print("  ESC = quit without saving")

        while manual_control.running:
            key = get_key_nonblocking()
            if not key:
                time.sleep(0.01)
                continue

            key_lower = key.lower()

            if key_lower == 'w':
                manual_control.is_moving_forward = True
            elif key_lower == 's':
                manual_control.is_moving_backward = True
            elif key_lower == 'e':
                manual_control.continuous_forward = not manual_control.continuous_forward
                if manual_control.continuous_forward:
                    manual_control.continuous_backward = False
            elif key_lower == 'd':
                manual_control.continuous_backward = not manual_control.continuous_backward
                if manual_control.continuous_backward:
                    manual_control.continuous_forward = False
            elif key_lower == ' ':
                manual_control.is_moving_forward = False
                manual_control.is_moving_backward = False
                manual_control.continuous_forward = False
                manual_control.continuous_backward = False
            elif key == '\r':  # ENTER
                dump_to_json(manual_control.x_axis, manual_control.y_axis)
                print("Position saved, exiting calibration...")
                manual_control.running = False
            elif key == '\x1b':  # ESC
                manual_control.running = False

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def start_calibration_control():
    """Start the motor control thread and terminal listener."""
    try:
        reset_manual_state()

        manual_control.running = True

        motor_thread = threading.Thread(target=manual_control.motor_control_loop, daemon=True)
        motor_thread.start()

        calibration_listener()

        manual_control.running = False
        manual_control.Motor1.Stop()
        print("Calibration exited cleanly.")

    except Exception as e:
        print(f"Error in calibration control: {e}")


def calibrate():
    """Entry point for calibration."""
    print("Starting calibration in 2 seconds...")
    time.sleep(2)
    start_calibration_control()
