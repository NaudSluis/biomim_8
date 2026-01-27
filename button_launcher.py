from gpiozero import Button
import subprocess
from signal import pause
import sys
import time

# Configure button with pull-up enabled (GPIO25 to GND)
try:
    button = Button(25, pull_up=True, bounce_time=0.01)
    print("✓ Button initialized successfully on GPIO25", flush=True)
except Exception as e:
    print(f"✗ Failed to initialize button: {e}", flush=True)
    sys.exit(1)

is_running = False  # This acts as our "lock"

def run_script():
    global is_running
    if is_running:
        print("Wash already in progress. Ignoring press.", flush=True)
        return
        
    is_running = True
    print(">>> BUTTON PRESSED - Starting wash...", flush=True)
    sys.stdout.flush()
    try:
        subprocess.run(["python3", "/home/naudsluis/biomim_8/motor_control/test_wash.py"])
    except Exception as e:
        print(f"Error running script: {e}", flush=True)
    finally:
        is_running = False  # Unlock when done
        print(">>> Wash finished. Ready for next press.", flush=True)
        sys.stdout.flush()

print("Button launcher started. Waiting for button press on GPIO25...", flush=True)
print("Button state (debug):", button.is_pressed, flush=True)
sys.stdout.flush()

button.when_pressed = run_script

# Also poll every 5 seconds to verify button is responding
print("Starting button monitoring loop...", flush=True)
try:
    while True:
        time.sleep(5)
        print(f"[{time.strftime('%H:%M:%S')}] Button state: {button.is_pressed}, Running: {is_running}", flush=True)
except KeyboardInterrupt:
    print("Button launcher stopped.", flush=True)
