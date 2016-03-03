#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

import neopixel
import paleopixel_spidev as paleopixel

# SuperPixel
# Author:  Mark Boszko
#
# Combines both NeoPixels and PaleoPixels (WS2801) into a single addressable
# SuperPixel type. Also allows merging of separate pixel strands into one
# master strand or grid.


# My LED strip configurations (for test):
NEOPIXEL_COUNT   = 244   # Number of NeoPixels in the strand
NEOPIXEL_PIN     = 18    # GPIO pin connected to the pixels (must support PWM!)
PALEOPIXEL_COUNT = 50    # Number of PaleoPixels in the strand

# My grid configuration (for test):
TIKI_NOOK_GRID = [(293, -9), (275, 10), (274, -10), (255, 10), (254, -11),
                  (243, -41), (162, 41), (161, -41), (80, 41), (79, -41), (0, 39)]

# Rows, bottom up: 39, -41, 41, -41,  41, -41, -11,  10, -10,  10,  -9
# Index, bottom up: 0,  79, 80, 161, 162, 243, 254, 255, 274, 275, 293

#####
# 
# SuperPixel - superset pixel strand class
# 
#####

def Color(red, green, blue):
    """Convert the provided red, green, blue color to a 24-bit color value.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    """
    return ((red & 0xFF) << 16) | ((green & 0xFF) << 8) | (blue & 0xFF)

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
# PixelGrid
# 
#####

class PixelGrid(object):
    def __init__(self, strand, *segments):
        """Represents a grid of pixels built from segments of LED strands.
        
        strand   - The pixel strand that these segments come from. Can be of
                   class Adafruit_NeoPixel, PaleoPixel, SuperPixel or compatible
        segments - Variable argument list of segments which should make up the
                   grid. The segments are tuples of (start_pixel, length), and
                   represents one horizontal row in the grid. Each row is added
                   from the top down to make a grid with origin 0,0 in the upper 
                   left.
                   
                   start_pixel - int, The left-most pixel in this row
                   length      - signed int, The number of pixels in this row,
                                 negative values representing a count backwards
                                 up the strand (to account for zig-zag layouts)
        
        WORK IN PROGRESS
        """
        self._strand = strand
        self._grid = []
        for segment in segments:
            print("segment: ", segment)
            # Create map
            start_pixel = segment[0]
            stop_pixel = segment[0] + segment[1]
            if (segment[1] < 0):
                step = -1
            else:
                step = 1
            row = []
            for pixel in range(start_pixel, stop_pixel, step):
                row.append({'pixel': pixel, "color": 0})
            self._grid.append(row)

    def __del__(self):
        # Clean up memory used by the library when not needed anymore.
        if self._strand is not None:
            self._strand = None
        if self._grid is not None:
            self._grid = None

    def begin(self):
        """Initialize _led_data to zeroes and set up any NeoPixels
        """
        self._strand.begin()
        self._strand.show()
        
    def show(self):
        """Update the display with the data from the LED buffer."""
        self._strand.show()

    def setPixelColor(self, x, y, color):
        """Set LED at position x, y to the provided 24-bit color value (in RGB order).
        """
        if (x >= len(self._grid)):
            return  # out of bounds; throw it away
        elif (y >= len(self._grid[x])):
            return  # We have to check the specific row because y isn't constant
            
        # Grid internal representation:
        self._grid[x][y]["color"] = color
        
        # Now also set it in the strand
        self._strand.setPixelColor(self._grid[x][y]["pixel"], self._grid[x][y]["color"])
        
    def setPixelColorRGB(self, x, y, red, green, blue):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setPixelColor(x, y, Color(red, green, blue))

    def getPixels(self):
        """Return the grid matrix as a 2D list.
        WARNING: Return value is NOT COMPATIBLE with what you would expect from
        a NeoPixel or PaleoPixel instance.
        """
        return self._grid
        
    def numRows(self):
        """Return the number of rows in the grid"""
        return len(self._grid)

    def numPixels(self):
        """Return the number of pixels in the display."""
        pixel_count = 0
        for row in self._grid:
            pixel_count = pixel_count + len(row)
        return pixel_count

    def getPixelColor(self, x, y):
        """Get the 24-bit RGB color value for the LED at position x, y."""
        return self._grid[x][y]["color"]
        

#####
#
# PixelMap - real world dimension map of pixels
#
#####

# TODO - PixelMap class


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
    strand = SuperPixel(strand1, strand2)
    
    # Intialize the SuperPixel strand (must be called once, before other 
    # functions, if the SuperPixel strand contains any NeoPixel sub-strands)
    strand.begin()
    
    # Create a pixel grid for same
    grid = PixelGrid(strand, TIKI_NOOK_GRID)

    print('Press Ctrl-C to quit.')
    while True:
        # Color wipe animations.
        #colorWipe(strand, Color(255, 0, 0))  # Red wipe
        #colorWipe(strand, Color(0, 255, 0))  # Green wipe
        #colorWipe(strand, Color(0, 0, 255))  # Blue wipe
        # Theater chase animations.
        #theaterChase(strand, Color(127, 127, 127))  # White theater chase
        #theaterChase(strand, Color(127,   0,   0))  # Red theater chase
        #theaterChase(strand, Color(  0,   0, 127))  # Blue theater chase
        # Rainbow animations.
        #rainbow(strand)
        #rainbowCycle(strand)
        #theaterChaseRainbow(strand)
        # Grid animations
        for row in grid.numRows():
            grid.setPixelColorRGB(row, 0, 255, 255, 255)
        grid.show()
