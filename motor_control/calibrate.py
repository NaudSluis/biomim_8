"""
Calibration script using the updated manual control setup.
No pynput dependency; works over SSH or local terminal.
"""
import select
import json
import time
import threading
import sys
import termios
import tty
from motor_control import manual_control


def get_key_nonblocking():
    """Get key press from keyboard"""
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None


def move_to_home():
    """
    Move both axes to their respective min endstops.
    Homing stops immediately when endstop is pressed.
    """
    print("Homing in progress...")
    # Homing speed: number of steps per iteration
    step_delay = 0.00001  # very small delay for fast homing

    # Y axis homing
    while not manual_control.y_min_pressed.is_set() and manual_control.running:
        manual_control.Motor1.TurnStep(Dir="backward", steps=1, stepdelay=step_delay)
        manual_control.y_axis -= 1

    print("Y axis homed.")

    # X axis homing
    while not manual_control.x_min_pressed.is_set() and manual_control.running:
        manual_control.Motor2.TurnStep(Dir="backward", steps=1, stepdelay=step_delay)
        manual_control.x_axis -= 1

    print("X axis homed.")

    # Reset counters after homing
    manual_control.x_axis = 0
    manual_control.y_axis = 0
    print("Homing complete.")


def reset_manual_state():
    """
    Reset motor step counters and flags in manual_control.
    Performs homing before calibration starts.
    """
    try:
        print("Resetting manual control state...")
        # Ensure motors are initialized
        manual_control.Motor1, manual_control.Motor2, manual_control.pump1, manual_control.pump2, manual_control.speed_control1, manual_control.speed_control2 = manual_control.initialize_motors()

        # Homing first
        move_to_home()

        # Stop any motion flags
        manual_control.is_moving_forward = False
        manual_control.is_moving_backward = False
        manual_control.continuous_forward = False
        manual_control.continuous_backward = False
        manual_control.is_moving_left = False
        manual_control.is_moving_right = False
        manual_control.continuous_left = False
        manual_control.continuous_right = False

        print("Manual state reset complete.")

    except Exception as e:
        print(f"Error resetting manual state: {e}")


def dump_to_json(x_axis, y_axis):
    """Save calibration positions to JSON."""
    coords = {"end position x": x_axis, "end position y": y_axis}
    print(coords)
    try:
        with open("motor_control/calibration_info.json", "w") as fp:
            json.dump(coords, fp)
        print("Calibration info saved to JSON.")
    except Exception as e:
        print(f"Error dumping to JSON: {e}")


def calibration_listener():
    """
    Terminal-based listener for calibration.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        print("Calibration controls:")
        print("  W = toggle continuous up")
        print("  A = toggle continuous left")
        print("  S = toggle continuous down")
        print("  D = toggle continuous right")
        print("  X = Step right")
        print("  Z = Step left")
        print("  Y = Step up")
        print("  H = Step Down")
        print("  SPACE = stop")
        print("  ENTER = save calibration")
        print("  ESC = quit")

        while manual_control.running:
            key = get_key_nonblocking()
            if not key:
                time.sleep(0.01)
                continue

            key_lower = key.lower()

            # Continuous movement toggles
            if key_lower == "w":
                manual_control.continuous_forward = not manual_control.continuous_forward
                if manual_control.continuous_forward:
                    manual_control.continuous_backward = False
                    manual_control.continuous_left = False
                    manual_control.continuous_right = False

            elif key_lower == "a":
                manual_control.continuous_left = not manual_control.continuous_left
                if manual_control.continuous_left:
                    manual_control.continuous_right = False
                    manual_control.continuous_forward = False
                    manual_control.continuous_backward = False

            elif key_lower == "s":
                manual_control.continuous_backward = not manual_control.continuous_backward
                if manual_control.continuous_backward:
                    manual_control.continuous_forward = False
                    manual_control.continuous_left = False
                    manual_control.continuous_right = False

            elif key_lower == "d":
                manual_control.continuous_right = not manual_control.continuous_right
                if manual_control.continuous_right:
                    manual_control.continuous_left = False
                    manual_control.continuous_forward = False
                    manual_control.continuous_backward = False

            # Single step movements
            elif key_lower == "z":
                manual_control.is_moving_left = True
            elif key_lower == "x":
                manual_control.is_moving_right = True
            elif key_lower == "y":
                manual_control.is_moving_forward = True
            elif key_lower == "h":
                manual_control.is_moving_backward = True

            elif key == " ":  # stop all movement
                manual_control.is_moving_forward = False
                manual_control.is_moving_backward = False
                manual_control.continuous_forward = False
                manual_control.continuous_backward = False
                manual_control.is_moving_left = False
                manual_control.is_moving_right = False
                manual_control.continuous_left = False
                manual_control.continuous_right = False

            elif key in ("\n", "\r"):  # ENTER = save calibration
                dump_to_json(manual_control.x_axis, manual_control.y_axis)
                print("Calibration saved, exiting...")
                manual_control.running = False

            elif key == "\x1b":  # ESC = quit
                manual_control.running = False

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def start_calibration_control():
    """
    Start the motor control thread and terminal listener.
    """
    try:
        reset_manual_state()

        manual_control.running = True

        motor_thread = threading.Thread(target=manual_control.motor_control_loop, daemon=True)
        motor_thread.start()

        calibration_listener()

        manual_control.running = False
        manual_control.Motor1.Stop()
        manual_control.Motor2.Stop()
        print("Calibration exited cleanly.")

    except Exception as e:
        print(f"Error in calibration control: {e}")


def calibrate():
    """Entry point for calibration."""
    print("Starting calibration in 2 seconds...")
    time.sleep(2)
    start_calibration_control()


if __name__ == "__main__":
    calibrate()
