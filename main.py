"""
Main control file for the robot control
"""

from motor_control.calibrate import calibrate
from motor_control.manual_control import start_manual_control 
from arduino_upload.uploader import upload_arduino_code
from motor_control.test_wash import demo


def main(answer: str):
    """
    Control function for robot

    :param answer: answer typed in by user via input
    :type answer: str
    """
    try:
        if answer not in ["a", "c", "t", "m"]:
            raise ValueError("Invalid input.")

        if answer == "a":
            upload_arduino_code()

        elif answer == "c":
            calibrate()

        elif answer == "t":
            demo()

        elif answer == "m":
            start_manual_control()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        answer = input("Upload Arduino (a), calibrate (c), test (t), manual (m)? ").strip().lower()

        if answer in ["a", "c", "t", "m"]:
            main(answer)
        else:
            print("Unknown answer, try again.\n")
