import serial
import time

def send_arduino_signal(signal):
    try:
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    try:
        ser.write(signal.encode('utf-8'))
        time.sleep(0.5)

        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Arduino Response: {line}")
    except Exception as e:
        print(f"Error during serial communication: {e}")
    finally:
        ser.close()

    return
