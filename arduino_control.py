import serial
import time
import sys

# In this file, connection is made via USB to the arduino. Also, there is a little interface that lets you
# decide whether you want to calibrate


def initialize_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate)
        time.sleep(2)  # Wait for the serial connection to initialize
        # ser.write(b'4')  # Send an initial command to the Arduino (if needed)
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}", flush=True)
        return None

def main():
    port = '/dev/ttyUSB0'
    baudrate = 9600
    ser = initialize_serial(port, baudrate)
    
    if ser is None:
        print("Failed to initialize serial connection.", flush=True)
        return
    
    

if __name__ == "__main__":
    main()
