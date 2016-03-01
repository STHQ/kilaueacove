#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

import neopixel
import paleopixel

# SuperPixel
# Author:  Mark Boszko
#
# Combines both NeoPixels and PaleoPixels (WS2801) into a single addressable
# SuperPixel type. Also allows merging of separate pixel strands into one
# master strand or array.


# My LED strip configurations (for test):
NEOPIXEL_COUNT   = 244   # Number of NeoPixels in the strand
NEOPIXEL_PIN     = 18    # GPIO pin connected to the pixels (must support PWM!)
PALEOPIXEL_COUNT = 50    # Number of PaleoPixels in the strand




# Main program logic follows:
if __name__ == '__main__':
	# Create NeoPixel object with appropriate configuration.
	strip1 = neopixel.Adafruit_NeoPixel(NEOPIXEL_COUNT, NEOPIXEL_PIN)
	strip2 = paleopixel.PaleoPixel(PALEOPIXEL_COUNT)
	# Intialize the library (must be called once for NeoPixels before other functions).
	strip1.begin()

	print 'Press Ctrl-C to quit.'
	while True:
		# Color wipe animations.
		paleopixel.colorWipe(strip1, Color(255, 0, 0))  # Red wipe
		paleopixel.colorWipe(strip2, Color(255, 0, 0))  # Red wipe
		paleopixel.colorWipe(strip1, Color(0, 255, 0))  # Blue wipe
		paleopixel.colorWipe(strip2, Color(0, 255, 0))  # Blue wipe
		paleopixel.colorWipe(strip1, Color(0, 0, 255))  # Green wipe
		paleopixel.colorWipe(strip2, Color(0, 0, 255))  # Green wipe
		# Theater chase animations.
		paleopixel.theaterChase(strip1, Color(127, 127, 127))  # White theater chase
		paleopixel.theaterChase(strip2, Color(127, 127, 127))  # White theater chase
		paleopixel.theaterChase(strip1, Color(127,   0,   0))  # Red theater chase
		paleopixel.theaterChase(strip2, Color(127,   0,   0))  # Red theater chase
		paleopixel.theaterChase(strip1, Color(  0,   0, 127))  # Blue theater chase
		paleopixel.theaterChase(strip2, Color(  0,   0, 127))  # Blue theater chase
		# Rainbow animations.
		paleopixel.rainbow(strip1)
		paleopixel.rainbow(strip2)
		paleopixel.rainbowCycle(strip1)
		paleopixel.rainbowCycle(strip2)
		paleopixel.theaterChaseRainbow(strip1)
		paleopixel.theaterChaseRainbow(strip2)