from gpiozero import Button
import time

button = Button(25, pull_up=True, bounce_time=0.01)

print("Waiting for button press on GPIO25...")

while True:
    if button.is_pressed:
        print("Button pressed!")
        time.sleep(0.5)  # Debounce
    time.sleep(0.05)
