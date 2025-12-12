import time
import threading
from pynput import keyboard
from DRV8825 import DRV8825


Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor1.SetMicroStep('softward', 'fullstep')


is_moving_forward = False
is_moving_backward = False

def on_press(key):
    global is_moving_forward, is_moving_backward
    try:
        if key.char == 'w':
            is_moving_forward = True
            is_moving_backward = False
        elif key.char == 's':
            is_moving_backward = True
            is_moving_forward = False
    except AttributeError:
        pass
    if key == keyboard.Key.esc:
        return False

def on_release(key):
    global is_moving_forward, is_moving_backward
    try:
        if key.char == 'w':
            is_moving_forward = False
            print('w')
        elif key.char == 's':
            is_moving_backward = False
    except AttributeError:
        pass
    if key == keyboard.Key.esc:
        return False

# Small-step movement functions
def step_motor_forward():
    Motor1.TurnStep(Dir='forward', steps=20, stepdelay=0.00002)

def step_motor_backward():
    Motor1.TurnStep(Dir='backward', steps=20, stepdelay=0.00002)

def motor_control_loop():
    """Continuously step the motor based on pressed keys."""
    while True:
        if is_moving_forward:
            step_motor_forward()
        elif is_moving_backward:
            step_motor_backward()
        else:
            time.sleep(0.01)

def start_manual_control():
    control_thread = threading.Thread(target=motor_control_loop, daemon=True)
    control_thread.start()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listening for keys... Press 'Esc' to exit.")
        listener.join()
    Motor1.Stop()
    print("Program exited.")

if __name__ == "__main__":
    start_manual_control()
 