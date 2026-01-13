from gpiozero import Button
from signal import pause

X_MIN_PIN = 17   # GPIO number, NOT physical pin

x_min = Button(X_MIN_PIN, pull_up=False)

x_min_hit = False  # variable you want to change

def on_x_min():
    global x_min_hit
    x_min_hit = True
    print("X min endstop hit, variable set to", x_min_hit)

x_min.when_pressed = on_x_min

pause()
