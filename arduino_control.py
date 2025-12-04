import serial
import time
import sys

def initialize_serial(port, baudrate):
    try:
        ser = serial.Serial(port, baudrate)
        time.sleep(2)  # Wait for the serial connection to initialize
        ser.write(b'4')  # Send an initial command to the Arduino (if needed)
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

    try:
        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    print(line)
            except OSError as e:
                print(f"Serial communication error: {e}", flush=True)
                ser.close()
                time.sleep(5)  # Wait for 5 seconds before retrying
                ser = initialize_serial(port, baudrate)
                if ser is None:
                    print("Failed to reinitialize serial connection.", flush=True)
                    return
    except KeyboardInterrupt:
        print("Exiting program", flush=True)
    finally:
        if ser is not None:
            ser.close()

if __name__ == "__main__":
    main()
