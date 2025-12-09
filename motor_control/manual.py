from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from pynput import keyboard
import time
import threading
import json
import busio

is_moving_forward = False
is_moving_down = False
is_moving_right = False
is_moving_left = False

x_axis = 0
y_axis = 0

# # 1. Initialize the I2C bus (required for both)
# i2c = busio.I2C(board.SCL, board.SDA)

# # 2. Initialize the FIRST HAT (uses the default address 0x60)
# # This connects to the HAT where you get stepper1 and stepper2
# kit1 = MotorKit(i2c=i2c, address=0x60) 
# motor1_stepper1 = kit1.stepper1
# motor1_stepper2 = kit1.stepper2

# # 3. Initialize the SECOND HAT (uses the changed address, e.g., 0x61)
# # You must physically set the jumpers on the second HAT to this address
# kit2 = MotorKit(i2c=i2c, address=0x61)
# motor2_stepper1 = kit2.stepper1 # The new motor 3
# motor2_stepper2 = kit2.stepper2 # The new motor 4
def dump_to_json(x_axis, y_axis):
    coords = {"end position x":x_axis, "end position y":y_axis}

    with open('calibration_info.json', 'w') as fp:
        json.dump(coords, fp)

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
    elif key == keyboard.Key.enter:
        # Call the save function using the current global values
        # Since dump_to_json uses the global axis variables, we can pass them.
        dump_to_json(x_axis, y_axis)
        print("Position is saved, exiting calibration mode...")
        time.sleep(1)
        return False

    if key.char == 'w':
        is_moving_forward = False
    elif key.char == 's':
        is_moving_down = False
    elif key.char == 'd':
        is_moving_right = False
    elif key.char == 'a':
        is_moving_left = False

def up():
    global y_axis
    # motor1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    # motor2.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    y_axis += 1
    print('forward')
    time.sleep(0.05)

def down():
    global y_axis
    # motor1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    # motor2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    y_axis -= 1
    print('backward')
    time.sleep(0.05) 

def right():
    global x_axis    
    # motor3.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    x_axis += 1
    print('right')
    time.sleep(0.05) 

def left():
    global x_axis   
    # motor3.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    x_axis -= 1
    print('left')
    time.sleep(0.05) 
    
def motor_control_loop():
    print("Ready to control")
    
    while True:
        if is_moving_forward:
            up()
        elif is_moving_down:
            down()
            
        elif is_moving_right:
            right()

        elif is_moving_left:
            left()
        else:
            # If not moving, still sleep briefly to prevent 100% CPU usage
            time.sleep(0.05)
    


def start_manual_control():
    control_thread = threading.Thread(target=motor_control_loop)
    control_thread.daemon = True # Allows the main program to exit even if this thread is running
    control_thread.start()
    
    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listening for key presses... Press 'Esc' to exit.")
        listener.join()
    print("Exiting program.")

if __name__ == "__main__":
    start_manual_control()
    
