# This file is used to upload code from the Pi to the arduino via Sruino CLI

import subprocess
import glob
import os

# group8 = pi name, biomim_8 dir name and wash_loop sketch dir. Make sure that the sketch dir has the same name as the sketch
SKETCH_DIR = "/home/group8/biomim_8/wash_loop"
FQBN = "arduino:avr:uno"


def find_serial_port():
    """
    Finds serial port with which the arduino is connected
    """
    ports = glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*")
    if not ports:
        raise RuntimeError("No Arduino detected")
    return ports[0]


def upload_arduino_code():
    """
    Uploads code to the Arduino via Arduino CLI
    """
    if not os.path.exists(SKETCH_DIR):
        raise FileNotFoundError(f"Sketch directory not found: {SKETCH_DIR}")

    port = find_serial_port()

    print(f"\nUploading wash_loop to {port}...\n")

    subprocess.run(["arduino-cli", "compile", "--fqbn", FQBN, SKETCH_DIR], check=True)

    subprocess.run(["arduino-cli", "upload", "-p", port, "--fqbn", FQBN, SKETCH_DIR], check=True)

    print("\nwash_loop upload complete\n")
