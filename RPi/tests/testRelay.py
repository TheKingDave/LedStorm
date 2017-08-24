import RPi.GPIO as gpio
from time import sleep

gpio.setmode(gpio.BCM)
gpio.setup(23, gpio.OUT)

try:
    on = True
    while True:
        if on:
            gpio.output(23, gpio.HIGH)
        else:
            gpio.output(23, gpio.LOW)
        print(on)
        sleep(1)
        on = not on
except KeyboardInterrupt:
    print("Closed by user")
finally:
    gpio.cleanup()
