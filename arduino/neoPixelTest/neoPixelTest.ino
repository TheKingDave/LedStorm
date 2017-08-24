#include "FastLED.h"

#define NUM_LEDS 200
//#define NUM_LEDS 25 * 5
#define LED_PIN 6

CRGB leds[NUM_LEDS];

void setup() {
  FastLED.addLeds<WS2812B, LED_PIN, RGB>(leds, NUM_LEDS);
  FastLED.setBrightness(64);
}

int count = 0;

int keepIn(int min, int max, int n) {
  if(n < min) {
    return keepIn(min, max, n + (max - min));
  }
  if(n > max) {
    return keepIn(min, max, n - (max - min));
  }
  return n;
}

void loop() {
  leds[keepIn(0, NUM_LEDS, count-3)] = CRGB::Black;
  leds[keepIn(0, NUM_LEDS, count-0)] = CRGB::White;
  FastLED.show();
  count++;
  count = keepIn(0, NUM_LEDS, count);
}

