import sys
import termios
import tty
import time
import threading
from DRV8825 import DRV8825

Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor1.SetMicroStep('softward', 'fullstep')

is_moving_forward = False
is_moving_backward = False
running = True

# ---------- Keyboard Input (SSH-safe) ----------
def get_key_nonblocking():
    """Read one key if available, otherwise return None."""
    import select
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

def keyboard_listener():
    global is_moving_forward, is_moving_backward, running

    # Make terminal read single characters
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    print("Listening for W/S (Esc to quit)...")

    try:
        while running:
            key = get_key_nonblocking()
            if key is None:
                time.sleep(0.01)
                continue

            key = key.lower()

            if key == "w":
                is_moving_forward = True
                is_moving_backward = False

            elif key == "s":
                is_moving_backward = True
                is_moving_forward = False

            elif key == "\x1b":  # ESC key
                running = False
                break

            # Key release simulation:
            # When another key is pressed, stop previous movement
            elif key.strip() == "":
                is_moving_forward = False
                is_moving_backward = False

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ---------- Motor Control Loop ----------
def step_motor_forward():
    Motor1.TurnStep(Dir='forward', steps=20, stepdelay=0.00002)

def step_motor_backward():
    Motor1.TurnStep(Dir='backward', steps=20, stepdelay=0.00002)

def motor_control_loop():
    global running
    while running:
        if is_moving_forward:
            step_motor_forward()
        elif is_moving_backward:
            step_motor_backward()
        else:
            time.sleep(0.01)

# ---------- Main ----------
def start_manual_control():
    global running
    running = True

    # Start motor thread
    motor_thread = threading.Thread(target=motor_control_loop, daemon=True)
    motor_thread.start()

    # Start input thread
    keyboard_listener()

    # Cleanup
    running = False
    Motor1.Stop()
    print("Program exited.")

if __name__ == "__main__":
    start_manual_control()
