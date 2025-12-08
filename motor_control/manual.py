from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from pynput import keyboard
import time

# Initialize the MotorKit
# Stepper 1 is connected to port M1/M2 (stepper 1)
kit = MotorKit()
motor1 = kit.stepper1

    # # Stepper 2 is connected to port M3/M4 (stepper 2)
motor2 = kit.stepper2

motor3 = 'x'

def on_press(key):
    """
    Callback function that is executed whenever a key is pressed.
    """
    try:
        if key == 'w':
            # Move both motors forward one step at the same time
            motor1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
            motor2.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)

        elif key == 's':
            # Move both motors backward one step at the same time
            motor1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
            motor2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
            
        elif key == 'd':
            # motor 3 moves forwards
            motor3.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)

        elif key == 'a':
            # Only motor 3 moves backwards
            motor3.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    except AttributeError:
        print(f"Special key pressed: {key}")

def on_release(key):
    """
    Callback function that is executed whenever a key is released.
    """
    if key == keyboard.Key.esc:
        # Stop listener
        return False

if __name__ == "__main__":
    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        print("Listening for key presses... Press 'Esc' to exit.")
        listener.join()
    print("Exiting program.")
