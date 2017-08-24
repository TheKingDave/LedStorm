import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

GPIO.setup(23, GPIO.OUT)

try:
    while True:
        GPIO.output(23, GPIO.HIGH)
        sleep(1)
        GPIO.output(23, GPIO.LOW)
        sleep(1)
except KeyboardInterrupt:
    print "Stopped by user"

GPIO.cleanup()