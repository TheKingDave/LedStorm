from time import sleep
from neopixel import *

LED_COUNT   = 200     # Number of LED pixels.
LED_PIN     = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA     = 5       # DMA channel to use for generating signal (try 5)
LED_INVERT  = False   # True to invert the signal (when using NPN transistor level shift)
LED_BRIGHT  = 10      # Brightness of LED strip

#strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, 255, 0, ws.WS2811_STRIP_GRB)
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHT)
strip.begin()

for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(255, 255, 255))

strip.show()
sleep(1)

for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(0, 0, 0))

strip.show()