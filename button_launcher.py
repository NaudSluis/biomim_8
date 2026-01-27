from gpiozero import Button
from motor_control.test_wash import demo
from signal import pause
import sys

# Configure button on GPIO25
button = Button(25, pull_up=False, bounce_time=0.01)
is_running = False  # This acts as our "lock"

def run_script():
    global is_running
    if is_running:
        print("Wash already in progress. Ignoring press.", flush=True)
        return
        
    is_running = True
    print("Starting wash...", flush=True)
    try:
        demo()
    except Exception as e:
        print(f"Error running script: {e}", flush=True)
    finally:
        is_running = False  # Unlock when done
        print("Wash finished. Ready for next press.", flush=True)

button.when_pressed = run_script
pause()
