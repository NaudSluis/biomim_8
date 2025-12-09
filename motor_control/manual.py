from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from pynput import keyboard
import time
import threading

is_moving_forward = False
is_moving_down = False
is_moving_right = False
is_moving_left = False

kit = MotorKit()
motor1 = kit.stepper1

motor2 = kit.stepper2

motor3 = 'x'

def on_press(key):
    """
    Callback function that is executed whenever a key is pressed.
    """
    global is_moving_forward
    global is_moving_down
    global is_moving_right
    global is_moving_left
    if key == keyboard.Key.esc:
        return False 
    try:
        if key.char == 'w':
            is_moving_forward = True
        elif key.char == 's':
            is_moving_down = True
        elif key.char == 'd':
            is_moving_right = True
        elif key.char == 'a':
            is_moving_left = True

    except AttributeError:
        print(f"Special key pressed: {key}")

def on_release(key):
    """
    Callback function that is executed whenever a key is released.
    """
    global is_moving_forward
    global is_moving_down
    global is_moving_right
    global is_moving_left
    
    if key == keyboard.Key.esc:
        return False 
    try:
        if key.char == 'w':
            is_moving_forward = False
        elif key.char == 's':
            is_moving_down = False
        elif key.char == 'd':
            is_moving_right = False
        elif key.char == 'a':
            is_moving_left = False
            
    except AttributeError:
        print(f"Special key pressed: {key}")
    
def motor_control_loop():

    print("Motor control thread started.")
    while True:
        if is_moving_forward:
            print('forward')
            # motor1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
            # motor2.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
            time.sleep(0.05) 
        elif is_moving_down:
            # motor1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
            # motor2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
            time.sleep(0.05) 
            print('backward')
        elif is_moving_right:
            # motor3.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
            time.sleep(0.05) 
            print('right')
        elif is_moving_left:
            # motor3.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
            time.sleep(0.05) 
            print('left')
        else:
            # If not moving, still sleep briefly to prevent 100% CPU usage
            time.sleep(0.05)

if __name__ == "__main__":
    control_thread = threading.Thread(target=motor_control_loop)
    control_thread.daemon = True # Allows the main program to exit even if this thread is running
    control_thread.start()
    
    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listening for key presses... Press 'Esc' to exit.")
        listener.join()
    print("Exiting program.")
