from gpiozero import Button
from motor_control.test_wash import demo
from signal import pause
import sys
import logging

# Setup logging to file since we can't see stdout in background
logging.basicConfig(
    filename='/home/group8/biomim_8/button_launcher.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Button launcher started")

# Configure button on GPIO25 (wired to GND)
try:
    button = Button(25, pull_up=True, bounce_time=0.01, active_high=False)
    logging.info("Button initialized on GPIO25")
except Exception as e:
    logging.error(f"Failed to initialize button: {e}")
    sys.exit(1)

is_running = False  # This acts as our "lock"

def run_script():
    global is_running
    logging.info(f"Button pressed. is_running={is_running}")
    if is_running:
        logging.info("Wash already in progress. Ignoring press.")
        return
        
    is_running = True
    logging.info("Starting wash...")
    try:
        demo()
        logging.info("Demo completed successfully")
    except Exception as e:
        logging.error(f"Error running script: {e}", exc_info=True)
    finally:
        is_running = False  # Unlock when done
        logging.info("Wash finished. Ready for next press.")

button.when_pressed = run_script
logging.info("Button callback registered. Waiting for presses...")
pause()
