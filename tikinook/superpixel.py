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

class SuperPixel(object):
    def __init__(self, *strands):
        """Class to represent a superset of both neopixel and paleopixel strands
        
        strands - Variable argument list of sub-strands which should make up
                  the one SuperPixel strand. The sub-strands are added to the
                  super-strand in the order the arguments are listed.
        """
        self._strands = strands
        pixel_count = 0
        for strand in self._strands:
            pixel_count = pixel_count + strand.numPixels()
        
        # Create an array for all of the LED color data
        self._led_data = [0] * pixel_count

    def __del__(self):
        # Clean up memory used by the library when not needed anymore.
        if self._led_data is not None:
            self._led_data = None
        if self._strands is not None:
            self._strands = None

    def begin(self):
        """Initialize _led_data to zeroes and set up NeoPixels
        """
        for strand in self._strands:
            strand.begin()
        self.show()
        
    def show(self):
        """Update the display with the data from the LED buffer."""
        for strand in self._strands:
            strand.show()

    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order).
        """
        if (n >= len(self._led_data)):
            return  # out of bounds; throw it away
            
        # SuperPixel internal representation:
        self._led_data[n] = color
        
        # Now also set it in the sub-strand
        pixel_offset = 0
        pixel_max    = 0
        for strand in self._strands:
        # TODO: Determine which strand this pixel is a part of, and set it.
            pixel_max = pixel_offset + strand.numPixels()
            if (pixel_offset <= n) and (n < pixel_max):
                pixel = n - pixel_offset
                strand.setPixelColor(pixel, color)
                break
            else:  # Must be in the next one
                pixel_offset = pixel_offset + strand.numPixels()

    def setPixelColorRGB(self, n, red, green, blue):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setPixelColor(n, Color(red, green, blue))

    def getPixels(self):
        """Return an object which allows access to the LED display data as if 
        it were a sequence of 24-bit RGB values.
        """
        return self._led_data

    def numPixels(self):
        """Return the number of pixels in the display."""
        return len(self._led_data)

    def getPixelColor(self, n):
        """Get the 24-bit RGB color value for the LED at position n."""
        return self._led_data[n]


        
#####
# 
# Test functions which animate LEDs in various ways.
# 
#####
         
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater marquee style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(((i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater marquee style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)
     
     
       
#####      
#      
# Let's test it out!
#
#####

# Main program logic follows:
if __name__ == '__main__':
    # Create pixel strands with appropriate configuration.
    strand1 = neopixel.Adafruit_NeoPixel(NEOPIXEL_COUNT, NEOPIXEL_PIN)
    strand2 = paleopixel.PaleoPixel(PALEOPIXEL_COUNT)
    
    # Combine them into one SuperPixel strand
    strand = SuperPixel(strand1)
    
    # Intialize the SuperPixel strand (must be called once, before other 
    # functions, is the SuperPixel strand contains any NeoPixels)
    strand.begin()

    print('Press Ctrl-C to quit.')
    while True:
        # Color wipe animations.
        colorWipe(strand, Color(255, 0, 0))  # Red wipe
        colorWipe(strand, Color(0, 255, 0))  # Blue wipe
        colorWipe(strand, Color(0, 0, 255))  # Green wipe
        # Theater chase animations.
        theaterChase(strand, Color(127, 127, 127))  # White theater chase
        theaterChase(strand, Color(127,   0,   0))  # Red theater chase
        theaterChase(strand, Color(  0,   0, 127))  # Blue theater chase
        # Rainbow animations.
        rainbow(strand)
        rainbowCycle(strand)
        theaterChaseRainbow(strand)