## User manual
Hi! This is a manual about the washing robot, where you will hopefully find everything you need. This manual is written for someone who uses Linux, so some (most) of the terminal code might not work on Windows

#### Table of contents
1. Explaination of hardware system
2. Use in pactice
3. Error handeling
3. FAQ
4. Contact information



#### Explaination of the system

The goal of this robot is to clean the window of the Mini-DOAS as good as possible. For this, it uses the following hardware (only inluding actuating and controlling hardware):

- 1x RPi5 (with SD)
- 1x Waveshare Stepper HAT
- 1x L298N motor driver module
- 1x NEMA17 1.8 degree stepper motor
- 1x 28BYJ-48 5v stepper motor
- 1x 12v waterpump
- 1x Continuous servo 5v
- 2x Mechanical stops
- 1x powersupply RPi5
- 1x Powersupply Stepper HAT (9-12v, 2-3A)
- 1x Powersupply L298N 12v

The Pi forms the basis of the system. The stepper HAT is mounted on top of the Pi, to which the NEMA17 and 28BYJ-48 are attached. In the image below you can find how the rest of the hardware should be connected to the pins. !NOTE, give some tips

![RPI5 Pin layout scheme](pin_layout.png)


#### Use in pactice

Before setting up the Hardware (or atleast more than you can carry to a watersafe location), connect your laptop to the Pi via ssh. You can use this [turtorial](https://www.raspberrypi.com/documentation/computers/remote-access.html#ssh) for example. 

Before we connect the stepper HAT to the Pi, make the stepper HAT compatible for both the 2-3A NEMA17 and the 500mA 28BYJ-48. Do this by checking the current through M1 and M2 and adjusting where needed, as described in the [HAT's own documentation](https://www.waveshare.com/wiki/Stepper_Motor_HAT#Current_Setting). Make sure to attach the HAT's powersupply and switching the power to 'On'. 

If you do not check this beforehand, you risk that either one is getting to low or, in the case of the small stepper, to high of a current; the latter results in overheating.

![Waveshare steper HAT](stepperhat_layout.png)

Attach the NEMA17 to the white A2-A1-B1-B2-insert, as seen in the top of the image of the HAT. Attacht the small stepper motor the to male 5V-A3-B3-A4-B4 insert (the red wire should go into the 5v).

Wire the rest of hardware as in the pin layout given above. 

Now attach the controlwires for the L298N, using the using the pin list below to their corresponding pin denoted on the driver module:

* IN1 = 9
* IN2 = 10

Also attach the 12v powersupply to the driver module.

To the pump, attach the tubes and run them through the bottomplate. Attach the nozzle to the tube and then the nozzle to the clip on the side of the hood.

Make sure the endstops are fitted to the underside of the rail and the back of the servo holder. The endstops are VERY important for the program, as these are an all-stop when their hit. If they are not pressed, the motor will just continue to turn.

Activating the program can be a bit of a hassle. For our demonstration, we attached a button to the system, which activates the full cycle when pressed. This is nice, but there are also programs for manual_control and calibration. The manual_control and calibration mode do, right now, not work in combination with the button. The reason for this, is that when the button mode is on, the Pi is constantly listening on the GPIO process for a press of the button. That means, that when you try to start either the manual or calibration mode, it says that GPIO is busy. 

So, when you want to start the manual or calibration mode, make sure to fist check ```sudo systemctl status wash_button.service```. If it is inactive, leave it be. If it is active, use ```sudo systemctl stop wash_button.service```, to stop it. Now move to the biomim_8 directory and type ```python3 main.py``` and choose one of the mode. 'test(t)'

If you want to start the button mode, use ```sudo systemctl start wash_button.service``` and check with ```sudo systemctl status wash_button.service```. 

#### Error Handeling/Quirks
- GPIO busy: A GPIO pin is being used, make sure the button mode is off (```sudo systemctl status wash_button.service```) or try kill the program and restart.
- For some reason, the program won't kill anymore with Crtl + C, using Crtl + \ always works
- The code uses threading for motor control; improper shutdown may leave threads running or GPIO pins in an undefined state.

#### Contact information

- Pepijn ten Hoor ()
- Tijl Smeets ()
- Mahitaap Ahmed ()
- Naud Sluis (naud.sluis@gmail.com)




