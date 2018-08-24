#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Adafruit NeoPixel library port to control the older WS2801 pixels from
  Raspberry Pi hardware SPI. Includes Adafruit “strandtest”-style functions
  and performs a self-test if run as main.

Not 100% compatible, as it uses [r, g, b] arrays for 'color' instead of
24-bit values.


Author: Mark Boszko (boszko+paleopixel@gmail.com)

Raspberry Pi SPI driver code for WS2801 pixels based on Adafruit_LEDpixels.py
https://github.com/adafruit/Adafruit-Raspberry-Pi-Python-Code

Python port of NeoPixel library based on the rpi_ws281x library port,
  by Tony DiCola and Jeremy Garff
https://github.com/jgarff/rpi_ws281x


Usage:

You'll need to translate 3.3V SPI logic levels from the Raspberry Pi to 5V.
Several options are possible, and I have a suggested circuit on my blog post
that describes this project in more detail:

http://stationinthemetro.com/2016/02/27/tiki-nook-build-part-2-raspberry-pi-led-control

- Connect the RPi's MOSI output to the SDI (Serial Data Input) on the WS2801s
- Connect the RPi SCLK clock output to CKI (ClocK Input) on the WS2801
- The RPi's 5V pins will probably not be enough to power a string of
    any significant length. Use an external power supply of appropriate amperage
- Be sure to connect the RPi ground to the LED strip's ground


License:

Licensed under The MIT License (MIT). Please see LICENSE.txt for full text
of the license.


Version History:

- 2.0.0 - 2018-08-22 - Updating to use Adafruit_WS2801, for Python 3, removing Numpy
- 1.1.0 - 2016-05-08 - Updated to use numpy for the internal arrays, for
                       speed improvements
- 1.0.1 - 2016-02-29 - Changed license from CC-BY-4.0 to MIT, due to
                       recommendation by Creative Commons not to apply their
                       licenses to software. See CC's FAQ for details:
                       https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software
- 1.0.0 - 2016-02-27 - Started development and complete rewrite, all in the
                       same day!

"""

import time

# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

# LED strip configuration:
LED_COUNT = 50  # Number of LED pixels.


#####
#
# PaleoPixel - NeoPixel library port for WS2801 control over RPi hardware SPI
#
#####

def Color(red, green, blue):
    """Return the provided red, green, blue colors as a list.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    red, green, blue: int, 0-255
    return: list
    """
    rgb = [red, green, blue]
    return rgb


class PaleoPixel(object):
    def __init__(self, num):
        """Class to represent a WS2801 LED display.

        num: int, number of pixels in the display strand.
        """
        # Specify a hardware SPI connection on /dev/spidev0.0:
        SPI_PORT = 0
        SPI_DEVICE = 0
        self.ws2801_strand = Adafruit_WS2801.WS2801Pixels(num, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

    def __del__(self):
        # Clean up memory used when not needed anymore.
        if self.ws2801_strand is not None:
            self.ws2801_strand = None

    def begin(self):
        """Initialize _led_data to zeroes, and show strand.
        Not necessary, since we do this in __init__, but handy.
        Mostly included for NeoPixel compatibility.
        """
        # Clip all values to zero
        self.ws2801_strand.clear()
        self.ws2801_strand.show()

    def show(self):
        """Update the display with the data from the LED buffer."""
        self.ws2801_strand.show()

    def setPixelColor(self, n, color):
        """Set LED at position n to the provided list (in RGB order).
        n: int
        color: list, as [R, G, B]
        """
        self.setPixelColorRGB(n, color[0], color[1], color[2])

    def setPixelColorRGB(self, n, red, green, blue):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        n: int, pixel position
        red, green, blue: int, 0-255
        """
        if n >= self.numPixels():
            # outside the strand length; throw it away
            pass
        else:
            self.ws2801_strand.set_pixel_rgb(n, red, green, blue)

    def getPixels(self):
        """Return a list of tuples which allows access to the LED data
        as [(R, G, B), ...]
        """
        pixels_rgb = []
        for pixel_index in range(self.ws2801_strand.count()):
            pixel_rgb = self.ws2801_strand.get_pixel_rgb(pixel_index)
            pixels_rgb.append(pixel_rgb)
        return pixels_rgb

    def numPixels(self):
        """Return the number of pixels in the display."""
        # print("numPixels: {}", self.ws2801_strand.count())
        return self.ws2801_strand.count()

    def getPixelColor(self, n):
        """Get a tuple with (R, G, B) color values for the LED pixel
        at position n.
        """
        return self.ws2801_strand.get_pixel_rgb(pixel_index)


#####
#
# Test functions which animate LEDs in various ways.
#
#####

def colorWipe(strip, color, wait_ms=20):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater marquee style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                # print("i: {}, q: {}, i+q: {}", i, q, i+q)
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, Color(0, 0, 0))


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
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) % 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=2):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(((i * 256 // strip.numPixels()) + j) % 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater marquee style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, Color(0, 0, 0))


#####
#
# Let's test it out!
#
#####

# Main program logic follows:
if __name__ == '__main__':
    # Create PaleoPixel object with appropriate number of LEDs.
    strip = PaleoPixel(LED_COUNT)
    # Reset the strand (does not actually need to be called before
    # other functions, but we're testing here).
    strip.begin()

    print('Press Ctrl-C to quit.')
    while True:
        # Color wipe animations.
        colorWipe(strip, Color(255, 0, 0), 0)  # Red wipe
        colorWipe(strip, Color(0, 255, 0), 0)  # Green wipe
        colorWipe(strip, Color(0, 0, 255), 0)  # Blue wipe
        # Theater chase animations.
        theaterChase(strip, Color(127, 127, 127))  # White theater chase
        theaterChase(strip, Color(127, 0, 0))  # Red theater chase
        theaterChase(strip, Color(0, 127, 127))  # Green theater chase
        theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
        # Rainbow animations.
        rainbow(strip)
        rainbowCycle(strip)
        theaterChaseRainbow(strip)
