import RPi.GPIO as gpio
from time import sleep

gpio.setmode(gpio.BCM)
gpio.setup(23, gpio.IN)

try:
    while True:
        print(gpio.input(23))
        sleep(0.5)
except KeyboardInterrupt:
    print("Close by user")
finally:
    gpio.cleanup()
