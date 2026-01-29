import sys
import os

# --- FIX PATH ---
# Add parent directory to path so we can import 'motor_control' package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
from motor_control import manual_control
from motor_control.calibrate import move_to_home, reset_manual_state
from motor_control.manual_control import (
    initialize_motors,
    pump_one_forward,
    rotate_sponge,
    move_to_position,
)
from DRV8825 import DRV8825
import time
import serial
from datetime import datetime
import threading
from gpiozero import Button, Device
from gpiozero.pins.rpigpio import RPiGPIOFactory
import signal

# Set pin factory at the very top
Device.pin_factory = RPiGPIOFactory()

# Global lock to prevent concurrent demo runs
is_running = False

# Graceful shutdown event
shutdown_event = threading.Event()

def handle_shutdown(signum, frame):
    print(f"Received signal {signum}, shutting down.")
    shutdown_event.set()

signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# ===================== Calibration Data Retrieval =====================

def get_calibrated_postion(json_file: str):
    """
    Retrieves earlier calibrated position
    """
    try:
        with open(json_file, "r") as fp:
            coords = json.load(fp)
            calibrated_x = int(coords["end_position_x"])
            calibrated_y = int(coords["end_position_y"])

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


# ===================== Wash Cycle =====================

def demo():
    """
    Performs one washing cycle and logs to json
    """
    global is_running
    
    # Initialize motors
    Motor1, Motor2, pump1 = initialize_motors()
    manual_control.Motor1 = Motor1
    manual_control.Motor2 = Motor2
    manual_control.pump1 = pump1

    # Initialize servo
    try:
        manual_control.servo = manual_control.Servo(26)
        manual_control.servo.detach() 
    except Exception as e:
        print(f"Servo init failed: {e}")
        manual_control.servo = None

    # Initialize endstops
    y_min = Button(manual_control.Y_MIN_PIN, pull_up=False)
    x_min = Button(manual_control.X_MIN_PIN, pull_up=True)

    y_min.when_pressed = manual_control.on_y_min_pressed
    y_min.when_released = manual_control.on_y_min_released

    x_min.when_pressed = manual_control.on_x_min_pressed
    x_min.when_released = manual_control.on_x_min_released

    manual_control.running = True

    # Start motor control loop thread
    motor_thread = threading.Thread(
        target=manual_control.motor_control_loop, daemon=True
    )
    motor_thread.start()

    # Give thread time to start
    time.sleep(0.1)

    start = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        move_to_home()

        # --- FIX: USE ABSOLUTE PATH ---
        # This finds the directory where THIS script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # This joins the directory with the filename
        json_path = os.path.join(script_dir, "calibration_info.json")
        house_json_path = os.path.join(script_dir, "calibration_house.json")
        
        print(f"Looking for calibration file at: {json_path}") # Debug print

        calibrated_x, calibrated_y = get_calibrated_postion(json_path)
        calibrated_x_house, calibrated_y_house = get_calibrated_postion(house_json_path)

        if calibrated_x is None or calibrated_y is None:
            print("Calibration data is invalid.")
            return

        move_to_position(0, calibrated_y)  # Move to spray position
        pump_one_forward(duration=10)
        move_to_position(calibrated_x, 0)
        time.sleep(5)
        rotate_sponge()
        move_to_position(-calibrated_x, 0)  # Move back to spray
        pump_one_forward(duration=10)
        move_to_home()
        move_to_position(calibrated_x_house, calibrated_y_house)  # Move to house position

    except Exception as e:
        print(f"Error during demo: {e}")
        
    finally:
        # --- CLEANUP & UNLOCK ---
        manual_control.running = False

        # Safely stop motors
        try:
            if "Motor1" in locals(): Motor1.Stop()
            if "Motor2" in locals(): Motor2.Stop()
        except Exception as e:
            print(f"Error stopping motors: {e}")

        # Clean up GPIO pins
        try:
            if "Motor1" in locals() and hasattr(Motor1, "dir_pin") and Motor1.dir_pin:
                Motor1.dir_pin.close()
            if "Motor1" in locals() and hasattr(Motor1, "step_pin") and Motor1.step_pin:
                Motor1.step_pin.close()
            if "Motor1" in locals() and hasattr(Motor1, "enable_pin") and Motor1.enable_pin:
                Motor1.enable_pin.close()

            if "Motor2" in locals() and hasattr(Motor2, "dir_pin") and Motor2.dir_pin:
                Motor2.dir_pin.close()
            if "Motor2" in locals() and hasattr(Motor2, "step_pin") and Motor2.step_pin:
                Motor2.step_pin.close()
            if "Motor2" in locals() and hasattr(Motor2, "enable_pin") and Motor2.enable_pin:
                Motor2.enable_pin.close()

            if y_min: y_min.close()
            if x_min: x_min.close()
        except Exception as e:
            print(f"Error cleaning up GPIO: {e}")

        # Logging - Use Absolute Path here as well to be safe
        end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # Determine path for logging.json (assumed to be in same folder as script)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            log_path = os.path.join(script_dir, "logging.json")
            
            try:
                with open(log_path, "r") as fp:
                    logs = json.load(fp)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            logs.append({"start_time": start, "end_time": end})
            
            with open(log_path, "w") as fp:
                json.dump(logs, fp, indent=2)
        except Exception as e:
            print(f"Error logging data: {e}")

        # Unlock allows the button to be pressed again
        is_running = False


# --- Button setup and main loop ---
def main():
    # Configure button on GPIO23 (wired to GND)
    try:
        button = Button(23, pull_up=True, bounce_time=0.01)
        print("Button initialized on GPIO23")
    except Exception as e:
        print(f"Failed to initialize button: {e}")
        return

    def on_button_pressed():
        global is_running
        
        if is_running:
            print("Wash already in progress. Ignoring press.")
            return

        print("Button pressed! Starting demo thread...")
        
        is_running = True 
        demo_thread = threading.Thread(target=demo)
        demo_thread.start()

    button.when_pressed = on_button_pressed
    print("Button callback registered. Waiting for presses...")

    try:
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, shutting down.")
        shutdown_event.set()

    try:
        import motor_control.manual_control as manual_control
        manual_control.running = False
    except Exception:
        pass

    print("Exiting now.")
    sys.exit(0)

if __name__ == "__main__":
    main()