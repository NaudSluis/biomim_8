"""
DRV8825 driver rewritten using gpiozero
"""
from gpiozero import DigitalOutputDevice
import time

MotorDir = [
    'forward',
    'backward',
]

ControlMode = [
    'hardware',
    'software',
]

class DRV8825():
    def __init__(self, dir_pin, step_pin, enable_pin, mode_pins):
        # GPIOZero devices
        self.dir_pin = DigitalOutputDevice(dir_pin)
        self.step_pin = DigitalOutputDevice(step_pin)
        self.enable_pin = DigitalOutputDevice(enable_pin)
        self.mode_pins = [DigitalOutputDevice(p) for p in mode_pins]

    def digital_write(self, pin, value):
        """Set a DigitalOutputDevice high or low"""
        if isinstance(pin, list) or isinstance(pin, tuple):
            # multiple pins at once
            for p, v in zip(pin, value):
                p.value = v
        else:
            pin.value = value

    def Stop(self):
        """Disable the motor"""
        self.enable_pin.off()

    def SetMicroStep(self, mode, stepformat):
        """
        Set microstepping mode
        (1) mode:
            'hardware' : Use switches on the module
            'software' : Use software to control microstep pins
        (2) stepformat:
            'fullstep', 'halfstep', '1/4step', '1/8step', '1/16step', '1/32step'
        """
        microstep = {
            'fullstep':  (0, 0, 0),
            'halfstep':  (1, 0, 0),
            '1/4step':   (0, 1, 0),
            '1/8step':   (1, 1, 0),
            '1/16step':  (0, 0, 1),
            '1/32step':  (1, 0, 1)
        }

        print("Control mode:", mode)
        if mode == ControlMode[1]:  # software
            print("Setting microstep pins:", stepformat)
            self.digital_write(self.mode_pins, microstep[stepformat])

    def TurnStep(self, Dir, steps, stepdelay=0.005):
        """Turn motor a given number of steps"""
        if Dir == MotorDir[0]:  # forward
            self.enable_pin.on()
            self.dir_pin.off()
        elif Dir == MotorDir[1]:  # backward
            self.enable_pin.on()
            self.dir_pin.on()
        else:
            print("The dir must be: 'forward' or 'backward'")
            self.Stop()
            return

        if steps == 0:
            return

        for _ in range(steps):
            self.step_pin.on()
            time.sleep(stepdelay)
            self.step_pin.off()
            time.sleep(stepdelay)
