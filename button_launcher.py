from gpiozero import Button
import subprocess
from signal import pause

button = Button(25)
is_running = False  # This acts as our "lock"

def run_script():
    global is_running
    if is_running:
        print("Wash already in progress. Ignoring press.")
        return
        
    is_running = True
    print("Starting wash...")
    subprocess.run(["python3", "/home/group8/biomim_8/motor_control/test_wash.py"])
    is_running = False  # Unlock when done
    print("Wash finished. Ready for next press.")

button.when_pressed = run_script
pause()