from gpiozero import Button
import subprocess
from signal import pause
import time

# Configure button with pull-up enabled (GPIO25 to GND)
button = Button(25, pull_up=True, bounce_time=0.01)
is_running = False  # This acts as our "lock"

def run_script():
    global is_running
    if is_running:
        print("Wash already in progress. Ignoring press.")
        return
        
    is_running = True
    print("Starting wash...")
    try:
        subprocess.run(["python3", "/home/naudsluis/biomim_8/motor_control/test_wash.py"])
    except Exception as e:
        print(f"Error running script: {e}")
    finally:
        is_running = False  # Unlock when done
        print("Wash finished. Ready for next press.")

print("Button launcher started. Waiting for button press on GPIO25...")
button.when_pressed = run_script

pause()