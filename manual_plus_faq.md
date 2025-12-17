## User manual
Hi! This is a manual about the washing robot, where you will hopefully find everything you need. This manual is written for someone who uses Linux, so some (most) of the terminal code might not work on Windows

#### Table of contents
1. Explaination of hardware system
2. Use in pactice
3. Error handeling
4. Contact information



#### Explaination of the system

The goal of this robot is to clean the window of the Mini-DOAS as good as possible. For this, it uses the following hardware (only inluding actuating and controlling hardware):

- 1x RPi5 (with SD)
- 1x Waveshare Stepper HAT
- 1x Keyestudio v4 (basically an Arduino UNO)
- 1x HW-130 Motor control shield with L293D driver
- 1x USB-A to USB-B Cable
- 1x NEMA17 1.8 degree stepper motor
- 1x 28BYJ-48 5v stepper motor
- 4x DC-motor (waterpumps) 3-5v
- 1x Continuous servo 5v
- 4x Mechanical stops
- 2x Waterflow sensors
- 1x powersupply RPi5
- 1x Powersupply Arduino
- 1x Powersupply Stepper HAT (12v, 2-3A)
- 1x Powersupply Motor control shield (5v)

The Pi forms the basis of the system. The stepper HAT is mounted on top of the Pi, to which the NEMA17 is attached. The other stepper is not attached to the HAT, due to the fact that it is a unipolor stepper instead of a bipolar (I read you could connect it if you would not use the middle gnd wire). To this HAT, attach the 12, 2-3A powersupply. Connect the Arduino via the USB cable and mount the Motor Shield on the Arduino. Screw in the 4 DC pumps, attach the servo and attach the steppermotor. Use a powersupply for both the arduino and the HAT, make sure the HAT does not get more than 7v, preferably a bit less. (**_NOTE:_** write about sensors and stops)

#### Use in pactice

Before setting up the Hardware (or atleast more than you can carry to a watersafe location), connect your laptop to the Pi via ssh. You can use this [turtorial](https://www.raspberrypi.com/documentation/computers/remote-access.html#ssh) for example. 

Setup the rest of the Hardware as above. (**_NOTE:_** write about tubes, nozzles, and the system in general)

To activate the program, move to the working directory and use ```python3 main.py``` to activate the system. Here you can choose to either upload now code to the Arduino (instead of doing it via the Arduino IDE UI), do a calibration, a test or use manual controls. 

If you just want to control the robot, use manual. If you want to calibrate the right position for autonomous washing, use calibration. To do a test run, use test! The controls will be displayed when activated. 

#### Error Handeling


```Error opening serial port '/dev/ttyUSB0': No such file or directory```  
This means that the Pi does not see that the arduino is connected via USB0. This can be either true, or it is in the port, but is does not see it. To get rid of the error, disconnect the cable, reboot the Arduino and reconnect the cable (rebooting the Pi is also possible, but that takes longer).

The reason the error occured for us was due to the fact that we ran more volt through it then the Arduino wanted, which is probably why it would disconnect itself. Make sure to use a powersupply of 5v, or a max of 7v (we did this a bit experimentally). 


```Error: invalid sketch name, the sketch name must match the folder name``` on Arduino  
This error occurs when the name of the Sketch (.ino) is not the same as the folder it is in. So match them!

#### Contact information

- Pepijn ten Hoor
- Tijl Smeets
- Mahitaap Ahmed
- Naud Sluis (naud.sluis@gmail.com)




