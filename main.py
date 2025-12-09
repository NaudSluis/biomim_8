# imports from other files
from motor_control.calibrate import calibrate
from motor_control.manual import start_manual_control


def main(answer:str):

    if answer == 'a':
        return answer
        # upload_arduino_code()
    elif answer == 'c':
        calibrate()
    elif answer == 't':
        return answer
        # functions to test
    elif answer == 'm':
        start_manual_control()

    return

if __name__ == "__main__":
    while True:
        answer = input("Would you like to upload arduino-code(a), calibrate(c), do a test(t), control manually(m)? ")
        if answer not in ['a', 'c', 't', 'm']:
            print('It looks like you gave an unknown answer, please try again \n')
        else:
            main(answer)