from gpiozero import Button
from signal import pause

X_MIN_PIN = 11

x_min = Button(X_MIN_PIN, pull_up=True)

def on_x_min():
    print("X min endstop hit")

x_min.when_pressed = on_x_min

pause()  # keeps the program alive
