#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

import cv2
import numpy
import subprocess

import neopixel
import paleopixel

# SuperPixel
# Author:  Mark Boszko
#
# Combines both NeoPixels and PaleoPixels (WS2801) into a single addressable
# SuperPixel type. Also allows merging of separate pixel strands into one
# master strand or grid.


# My LED strip configurations (for test):
NEOPIXEL_COUNT = 271  # Number of NeoPixels in the strand
NEOPIXEL_PIN = 18  # GPIO pin connected to the pixels (must support PWM!)
PALEOPIXEL_COUNT = 50  # Number of PaleoPixels in the strand

# My grid configuration (for test):
TIKI_NOOK_GRID = [(311, 10), (310, -10), (291, 10), (290, -10), (271, 10),
                  (247, 24),
                  (246, -41), (165, 41), (164, -41), (83, 41), (82, -41), (3, 39),
                  (0, 3)]


# Rows, bottom up: 39, -41, 41, -41,  41, -41, -11,  10, -10,  10,  -9
# Index, bottom up: 0,  79, 80, 161, 162, 243, 254, 255, 274, 275, 293

#####
#
# SuperPixel - superset pixel strand class
#
#####

# FIXME: We need to make sure that we use the RGB color functions for all pixel
# settings, because NeoPixels and PaleoPixels now use different internal
# color representations.
# PaleoPixel color = [R, G, B] numpy.array
# NeoPixel color = 24-bit color int

def Color(red, green, blue):
    """Return the provided red, green, blue colors as a numpy array.
    Each color component should be a value 0-255 where 0 is the lowest intensity
    and 255 is the highest intensity.
    red, green, blue: int, 0-255
    return: numpy.array
    """
    # "& 0xFF" is to make sure we're not exceeding max setting of 255
    # 2018-08-22 This seems to have an error with Python 3
    # rgb = numpy.array([red & 0xFF, green & 0xFF, blue & 0xFF])
    rgb = numpy.array([red, green, blue])
    return rgb


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

        # Create an array for all of the LED color data:
        # 2D numpyarray, LED count by 3 (RGB), type int
        self._led_data = numpy.zeros((pixel_count, 3), dtype=numpy.int)

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
            # Each strand knows how to show itself.
            strand.show()

    def setPixelColor(self, n, color_rgb):
        """Set LED at position n to the provided numpy array [R, G, B].
        n: int
        color: numpy.array, as [R, G, B]
        """
        if (n >= len(self._led_data)):
            return  # pixel 'n' is out of bounds; throw it away

        # SuperPixel internal representation:
        self._led_data[n] = color_rgb

        # Now also set it in the sub-strand
        pixel_offset = 0
        pixel_max = 0
        for strand in self._strands:
            # Determine which strand this pixel is a part of, and set it.
            pixel_max = pixel_offset + strand.numPixels()
            if (pixel_offset <= n) and (n < pixel_max):
                pixel = n - pixel_offset
                strand.setPixelColorRGB(pixel, color_rgb[0].item(), color_rgb[1].item(), color_rgb[2].item())
                break
            else:  # Must be in the next one
                pixel_offset = pixel_offset + strand.numPixels()

    def setPixelColorRGB(self, n, red, green, blue):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        n: int, pixel location
        red, green, blue: int, 0-255
        """
        self.setPixelColor(n, Color(red, green, blue))
        # self.setPixelColor(n, red, green, blue)

    def getPixels(self):
        """Return an object which allows access to the LED display data as if
        it were a sequence of 24-bit RGB values.
        """
        return self._led_data

    def numPixels(self):
        """Return the number of pixels in the display."""
        return len(self._led_data)

    def getPixelColor(self, n):
        """Get the [R, G, B] color array for the LED at position n.
        n: int
        """
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

        Internal representation: [row][column][strand_pixel, R, G, B]

        WORK IN PROGRESS
        """
        # TODO: Convert to numpy 3D array
        # TODO: Would this be more ifficient if I grabbed the strand pixel as
        #       an object, and there was no internal grid representation?
        self._strand = strand
        # Find maximum row width
        max_width = 0
        for segment in segments:
            row_width = abs(segment[1])
            if row_width > max_width:
                max_width = row_width
        # Create an empty grid array
        self._grid = numpy.zeros(shape=(len(segments), max_width, 4), dtype=numpy.int)
        # print("_grid: ", self._grid.shape)

        # Load up the grid with pixel location data
        row = 0
        for segment in segments:
            # print("segment: ", segment)
            # Create map
            start_pixel = segment[0]
            stop_pixel = segment[0] + segment[1]
            if (segment[1] < 0):
                step = -1
            else:
                step = 1
            column = 0
            for pixel in range(start_pixel, stop_pixel, step):
                self._grid[row][column] = [pixel, 0, 0, 0]
                column = column + 1
            row = row + 1
        # print("_grid: ", self._grid)

        # TODO: trim the rows that are smaller than max_width
        # How do we do this without accidentally trimming the 0th pixel?

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

    def setPixelColor(self, x=0, y=0, color_rgb=None):
        """Set LED at position x, y to the provided 24-bit color value (in RGB order).
        """
        if (y >= len(self._grid)):
            return  # out of bounds; throw it away
        elif (x >= len(self._grid[y])):
            return  # We have to check the specific row because y isn't constant

        # Grid internal representation:
        self._grid[y][x][1], self._grid[y][x][2], self._grid[y][x][3] = color_rgb

        # Now also set it in the strand
        self._strand.setPixelColorRGB(self._grid[y][x][0].item(), self._grid[y][x][1], self._grid[y][x][2],
                                      self._grid[y][x][3])

    def setPixelColorRGB(self, x, y, red, green, blue):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        color_rgb = Color(red, green, blue)
        # print("> About to call setPixelColor({}, {}, {})", x, y, color_rgb)
        self.setPixelColor(x=x, y=y, color_rgb=color_rgb)

    def setRowColor(self, row, color):
        """Set all row LEDs to the provided color values as [R, G, B]
        """
        # TODO: Seems like there may be a more efficient way to do this in numpy
        for x in range(len(self._grid[row])):
            self.setPixelColor(x, row, color)

    def setRowColorRGB(self, row, red, green, blue):
        """Set all LEDs to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setRowColor(row, Color(red, green, blue))

    def setAllColor(self, color):
        """Set all LEDs to the provided color values as [R, G, B]
        """
        # TODO: Seems like there may be a more efficient way to do this in numpy
        for y in range(len(self._grid)):
            for x in range(len(self._grid[y])):
                self.setPixelColor(x, y, color)

    def setAllColorRGB(self, red, green, blue):
        """Set all LEDs to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setAllColor(Color(red, green, blue))

    def getPixels(self):
        """Return the grid matrix as a 3D list.
        WARNING: Return value is NOT COMPATIBLE with what you would expect from
        a NeoPixel or PaleoPixel instance.
        """
        return self.getGrid()

    def getGrid(self):
        """Return the grid matrix as a 3D list.
        """
        return self._grid

    def numRows(self):
        """Return the number of rows in the grid"""
        return len(self._grid)

    def shape(self):
        """Return the shape of the grid"""
        # print("shape:", self._grid.shape)
        return self._grid.shape

    def numPixels(self):
        """Return the number of pixels in the display."""
        pixel_count = 0
        for row in self._grid:
            pixel_count = pixel_count + len(row)
        return pixel_count

    def getPixelColor(self, x, y):
        """Get the [R, G, B] color value array for the LED at position x, y."""
        red = self._grid[y][x][1]
        green = self._grid[y][x][2]
        blue = self._grid[y][x][3]
        return [red, green, blue]


#####
#
# PixelMap - real world dimension map of pixels
#
#####

# TODO - PixelMap class


#####
#
# PixelPlayer - load video to play on a grid
#
#####

class PixelPlayer(object):
    def __init__(self, grid, file):
        """Class for playing video on a grid of LED pixels.

        grid - The PixelGrid that the video will be played on. We need to know
               this, so that we only load data that will be used for the size
               of the grid.
        file - POSIX URL for the movie file to be loaded; can be relative

        Recommend that the file be a QuickTime .mov, Animation codec, for
        lossless animation quality. (It will play MPEG-4, but the compression is
        super noisy, and very noticeable on the LED pixels.)

        Pixels in the video should be 1:1 for LED pixels, and start at the left
        edge of the video frame. You may need to create a video in multiples of
        16x16 px, but any pixels outside the grid size will be ignored.

        WORK IN PROGRESS
        """
        self._grid = grid

        vid = cv2.VideoCapture(file)

        if (vid.isOpened()):
            print("Opened video")
        else:
            print("Open failed")

        frameCount = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = vid.get(cv2.CAP_PROP_FPS)
        print("frameCount: " + str(frameCount))
        print("fps: " + str(fps))

        waitPerFrameInSeconds = 1.0 / fps  # probably minus some overhead fudge factor

        # Load the pixel data
        # print("Loading video_data")
        grid_shape = self._grid.shape()
        self._video_data = numpy.zeros((frameCount, grid_shape[0], grid_shape[1], 3), dtype=numpy.int)

        frame_increment = 0
        for frame in range(frameCount):
            # Grabbing values from the frame tuple
            # 'ret' is a boolean for whether there's a frame at this index
            ret, frameImg = vid.read()
            if (ret):
                for y in range(self._video_data.shape[1]):
                    for x in range(self._video_data.shape[2]):
                        try:  # grid may be bigger than video
                            self._video_data[frame_increment][y][x] = [frameImg[y, x, 2], frameImg[y, x, 1],
                                                                       frameImg[y, x, 0]]
                        except IndexError:
                            pass
            frame_increment = frame_increment + 1
        vid.release()

    def __del__(self):
        # Clean up memory used by the library when not needed anymore.
        if self._grid is not None:
            self._grid = None
        if self._video_data is not None:
            self._video_data = None

    def play(self):
        """Plays the loaded data on the PixelGrid"""
        # print ("Displaying video_data")
        for frame in self._video_data:
            for y in range(frame.shape[0]):
                for x in range(frame.shape[1]):
                    self._grid.setPixelColor(x, y, frame[y][x])
            self._grid.show()


#####
#
# Strand Test functions which animate LEDs in various ways.
#
#####

def colorAll(strip, color):
    """Set color of entire strand at once."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()


def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=5):
    """Movie theater marquee style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
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
            strip.setPixelColor(i, wheel((i + j) & 255))  # FIXME
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=2):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(((i * 256 // strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater marquee style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))  # FIXME
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, Color(0, 0, 0))


#####
#
# Grid Test functions
#
#####

def colorWipeGrid(grid, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    theGrid = grid.getGrid()
    for y in range(len(theGrid)):
        for x in range(len(theGrid[y])):
            grid.setPixelColor(x, y, color)
            grid.show()
            time.sleep(wait_ms / 1000.0)


def boatGrid(grid, wait_ms=5000):
    """Mark port and starboard end pixels of each row with red and green."""
    theGrid = grid.getGrid()
    for y in range(len(theGrid)):
        grid.setPixelColorRGB(0, y, 255, 0, 0)
        end_x = len(theGrid[y]) - 1
        grid.setPixelColorRGB(end_x, y, 0, 255, 0)
        grid.show()
    time.sleep(wait_ms / 1000.0)


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
    grid = PixelGrid(strand, (284, 10), (283, -10), (264, 10), (263, -10), (244, 10), (243, -41), (162, 41), (161, -41),
                     (80, 41), (79, -41), (0, 39))
    rattan_grid = PixelGrid(strand, (284, 10), (283, -10), (264, 10), (263, -10), (244, 10))
    shelf_back_grid = PixelGrid(strand, (162, 41), (80, 41), (0, 39))
    shelf_front_grid = PixelGrid(strand, (243, -41), (161, -41), (79, -41))

    print('Press Ctrl-C to quit.')
    while True:
        # # Color wipe animations.
        colorWipe(strand, Color(255, 0, 0), 0)  # Red wipe
        time.sleep(1)
        colorWipe(strand, Color(0, 255, 0), 0)  # Green wipe
        time.sleep(1)
        colorWipe(strand, Color(0, 0, 255), 0)  # Blue wipe
        time.sleep(1)
        # # Theater chase animations.
        # theaterChase(strand, Color(127, 127, 127))  # White theater chase
        # theaterChase(strand, Color(127,   0,   0))  # Red theater chase
        # theaterChase(strand, Color(  0, 127,   0))  # Green theater chase
        # theaterChase(strand, Color(  0,   0, 127))  # Blue theater chase
        # # Rainbow animations.
        # rainbow(strand)
        # rainbowCycle(strand)
        # theaterChaseRainbow(strand)

        # Grid animations
        boatGrid(grid)  # port-starboard markers for each row
        time.sleep(1)
        colorWipeGrid(grid, Color(127, 127, 127), 5)  # White (50%) wipe
        time.sleep(1)
        colorWipeGrid(grid, Color(255, 0, 0), 5)  # Red wipe
        time.sleep(1)
        colorWipeGrid(grid, Color(0, 255, 0), 5)  # Green wipe
        time.sleep(1)
        colorWipeGrid(grid, Color(0, 0, 255), 5)  # Blue wipe
        time.sleep(1)
        colorWipeGrid(grid, Color(255, 255, 255), 5)  # White (100%) wipe
        time.sleep(1)

        # Use multiple grids at once, from the same strand
        # rattan_grid.setAllColorRGB(250, 127, 0)
#         rattan_grid.setRowColorRGB(3, 0, 90, 75)
#         rattan_grid.setRowColorRGB(4, 0, 0, 100)
#         shelf_back_grid.setAllColorRGB(2, 4, 8)
#         shelf_front_grid.setAllColorRGB(50, 20, 10)
#         rattan_grid.show()
#         shelf_back_grid.show()
#         shelf_front_grid.show()
#         time.sleep(5)
# 
#         boatGrid(rattan_grid)

# Load in the data from a QuickTime video

# test_animation = PixelPlayer(rattan_grid, 'animation/rgb-test-16x16-lossless.mov')
#         test_animation.play()
