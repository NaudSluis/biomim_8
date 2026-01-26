from gpiozero import Button
import subprocess
from signal import pause

# Initialize the button on GPIO 26
# GPIO Zero assumes the other end of the button is connected to GND
button = Button(26)

def run_script():
    print("Button pressed! Running test_wash.py...")
    # This runs your script as a separate process
    subprocess.run(["python3", "home/group8/biomim_8/motor_control/test_wash.py"])

# Link the press event to our function
button.when_pressed = run_script

print("System ready. Press the button to start the wash.")
pause() # Keeps the script running in the background