# imports from other files
from motor_control.calibrate import calibrate
from motor_control.manual_control import start_manual_control


def main(answer: str):
    try:
        if answer not in ['a', 'c', 't', 'm']:
            raise ValueError("Invalid input. Please enter 'a', 'c', 't', or 'm'.")

        if answer == 'a':
            # upload_arduino_code()
            return answer
        elif answer == 'c':
            calibrate()
        elif answer == 't':
            # functions to test
            return answer
        elif answer == 'm':
            start_manual_control()
    except ValueError as ve:
        print(ve)
    except Exception as e:
        print(f"An error occurred: {e}")

    return


if __name__ == "__main__":
    while True:
        answer = input("Would you like to upload arduino-code(a), calibrate(c), do a test(t), control manually(m)? ")
        if answer not in ['a', 'c', 't', 'm']:
            print('It looks like you gave an unknown answer, please try again \n')
        else:
            main(answer)