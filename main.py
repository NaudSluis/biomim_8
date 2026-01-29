"""
Main control file for the robot control
"""

from motor_control.calibrate import start_calibration_control
from motor_control.manual_control import start_manual_control
from motor_control.test_wash import demo


def main(answer: str):
    """
    Control function for robot

    :param answer: answer typed in by user via input
    :type answer: str
    """
    try:
        if answer not in ["c", "t", "m"]:
            raise ValueError("Invalid input.")

        if answer == "c":
            start_calibration_control()

        elif answer == "t":
            demo()

        elif answer == "m":
            start_manual_control()

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        answer = input("calibrate (c), test (t), manual (m)? ").strip().lower()

        if answer in ["c", "t", "m"]:
            main(answer)
        else:
            print("Unknown answer, try again.\n")
