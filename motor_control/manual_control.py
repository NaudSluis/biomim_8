import sys
import termios
import tty
import time
import serial
import threading
from .DRV8825 import DRV8825

Motor1 = DRV8825(dir_pin=13, step_pin=19, enable_pin=12, mode_pins=(16, 17, 20))
Motor1.SetMicroStep('softward', '1/32step')

is_moving_forward = False      # single step
is_moving_backward = False     # single step
continuous_forward = False     # toggle
continuous_backward = False    # toggle
y_axis = 0
x_axis = 0
running = True


def initialize_connection():
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}", flush=True)
        return ser

def send_arduino_signal(ser, signal):
    
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}", flush=True)

    try:
        ser.write(signal.encode('utf-8'))
        time.sleep(0.5)

        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Arduino Response: {line}", flush=True)
    except Exception as e:
        print(f"Error during serial communication: {e}", flush=True)
    finally:
        ser.close()
        print('serial closed')

    return

def get_key_nonblocking():
    import select
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if dr:
        return sys.stdin.read(1)
    return None

def keyboard_listener():
    global is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward, running
    
    ser = initialize_connection()

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
            elif key == "r":
                send_arduino_signal(ser, 'rotate')
            elif key == "z":
                send_arduino_signal(ser, 'pump_soap')
            elif key == "x":
                send_arduino_signal(ser, 'pump_water')
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
    Motor1.TurnStep(Dir='forward', steps=20, stepdelay=0.000001)

def step_motor_backward():
    Motor1.TurnStep(Dir='backward', steps=20, stepdelay=0.000001)

def motor_control_loop():
    global running, is_moving_forward, is_moving_backward
    global continuous_forward, continuous_backward
    global y_axis, x_axis

    while running:

        if is_moving_forward:
            step_motor_forward()
            y_axis += 1
            is_moving_forward = False

        elif is_moving_backward:
            step_motor_backward()
            y_axis -= 1
            is_moving_backward = False

        elif continuous_forward:
            step_motor_forward()
            y_axis += 1

        elif continuous_backward:
            step_motor_backward()
            y_axis -= 1


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
