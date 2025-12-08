# imports from other files


def main(answer:str):

    if answer == 'a':
        return answer
        # upload_arduino_code()
    elif answer == 'c':
        return answer
        # functions to calibrate
    elif answer == 't':
        return answer
        # functions to test
    elif answer == 'm':
        # functions to controll manually
        return answer

    return

if __name__ == "__main__":
    while True:
        answer = input("Would you like to upload arduino-code(a), calibrate(c), do a test(t), control manually(m)? ")
        if answer not in ['a', 'c', 't', 'm']:
            print('It looks like you gave an unknown answer, please try again \n')
        else:
            main(answer)