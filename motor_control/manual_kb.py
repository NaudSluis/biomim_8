import sys
import termios
import tty
import time
import threading
from DRV8825 import DRV8825

Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor1.SetMicroStep('softward', 'fullstep')

is_moving_forward = False      # single step
is_moving_backward = False     # single step
continuous_forward = False     # toggle
continuous_backward = False    # toggle
running = True

def get_key_nonblocking():
    import select
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

def keyboard_listener():
    global is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward, running

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    print("Controls:")
    print("  W = one step forward")
    print("  S = one step backward")
    print("  E = toggle continuous forward")
    print("  D = toggle continuous backward")
    print("  SPACE = stop")
    print("  ESC = quit")

    try:
        while running:
            key = get_key_nonblocking()
            if not key:
                time.sleep(0.01)
                continue

            key = key.lower()

            if key == "w":
                is_moving_forward = True

            elif key == "s":
                is_moving_backward = True

            elif key == "e":
                continuous_forward = not continuous_forward
                if continuous_forward:
                    continuous_backward = False  # stop opposite mode

            elif key == "d":
                continuous_backward = not continuous_backward
                if continuous_backward:
                    continuous_forward = False  # stop opposite mode

            elif key == " ":
                continuous_forward = False
                continuous_backward = False
                is_moving_forward = False
                is_moving_backward = False

            elif key == "\x1b":  # ESC
                running = False
                break

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def step_motor_forward():
    Motor1.TurnStep(Dir='forward', steps=20, stepdelay=0.000002)

def step_motor_backward():
    Motor1.TurnStep(Dir='backward', steps=20, stepdelay=0.000002)

def motor_control_loop():
    global running, is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward

    while running:

        if is_moving_forward:
            step_motor_forward()
            is_moving_forward = False

        elif is_moving_backward:
            step_motor_backward()
            is_moving_backward = False

        elif continuous_forward:
            step_motor_forward()

        elif continuous_backward:
            step_motor_backward()

        else:
            time.sleep(0.01)

def start_manual_control():
    global running

    running = True

    motor_thread = threading.Thread(target=motor_control_loop, daemon=True)
    motor_thread.start()

    keyboard_listener()

    running = False
    Motor1.Stop()
    print("Program exited.")

if __name__ == "__main__":
    start_manual_control()
