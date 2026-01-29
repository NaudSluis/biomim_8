from gpiozero import Button, Device
from gpiozero.pins.rpigpio import RPiGPIOFactory
from motor_control.test_wash import demo
import threading
import sys
import logging

import signal


# Setup logging to file since we can't see stdout in background
logging.basicConfig(
    filename='/home/group8/biomim_8/button_launcher.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Button launcher started")

# Graceful shutdown handler

shutdown_event = threading.Event()

def handle_shutdown(signum, frame):
    logging.info(f"Received signal {signum}, shutting down.")
    shutdown_event.set()

# Register signal handlers for SIGINT (Ctrl+C) and SIGTERM (systemd stop)
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

# Set pin factory BEFORE any Button is created
try:
    Device.pin_factory = RPiGPIOFactory()
    logging.info(f"Pin factory set to: {type(Device.pin_factory)}")
except Exception as e:
    logging.error(f"Failed to set pin factory: {e}")
    sys.exit(1)


# Configure button on GPIO23 (wired to GND)
try:
    button = Button(23, pull_up=True, bounce_time=0.01)
    logging.info(f"Button initialized on GPIO23, pin_factory={type(button.pin_factory)}")
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

# Robust event loop to keep the program alive and responsive to signals
def wait_forever():
    try:
        while not shutdown_event.is_set():
            shutdown_event.wait(1)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received, shutting down.")
        shutdown_event.set()

wait_forever()
