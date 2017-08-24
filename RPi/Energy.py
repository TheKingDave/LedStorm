import RPi.GPIO as GPIO

class Energy(object):

    def __init__(self, pin, invert):
        self.pin = pin
        self.invert = invert
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self.set_power(False)

    def set_power(self, on):
        if self.invert: on = not on
        power_ = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(self.pin, power_)

    def __del__(self):
        GPIO.cleanup()