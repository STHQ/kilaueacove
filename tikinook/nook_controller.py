#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Code specific to controlling the lights and other display events
in the tiki nook for Kilauea Cove.

Must be run from the current directory, else the animation will not load, as:
    sudo python nook_controller.py

Author: Mark Boszko (boszko+kilaueacove@gmail.com)

License:
Licensed under The MIT License (MIT). Please see LICENSE.txt for full text
of the license.

Version History:
- 0.2.0 - 2016-08-07 - Add the 3 button NeoPixels + the 24 ring NeoPixels
                       Fixed the red toggle detection + volcano show restriction
- 0.1.0 - 2016-05-07 - Started development
"""

import time
import RPi.GPIO as GPIO
import threading
import neopixel
import paleopixel
from superpixel import *

# Identify GPIO pins

BUTTON_WHITE_IN = 23
BUTTON_AMBER_IN = 24
BUTTON_RED_IN = 25
TOGGLE_RED_IN = 16
FISH_FLOAT = 20


# Set up GPIO pins

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_WHITE_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_AMBER_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RED_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TOGGLE_RED_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(FISH_FLOAT, GPIO.OUT)


# Set up the strand

# My LED strip configurations (for test):
WHITE_LED = 0            # These are the LEDs inside the buttons
AMBER_LED = 1
RED_LED = 2
NEOPIXEL_COUNT   = 271   # Number of NeoPixels in the strand
NEOPIXEL_PIN     = 18    # GPIO pin connected to the pixels (must support PWM!)
PALEOPIXEL_COUNT = 50    # Number of PaleoPixels in the strand

# Create pixel strands with appropriate configuration.
strand1 = neopixel.Adafruit_NeoPixel(NEOPIXEL_COUNT, NEOPIXEL_PIN)
strand2 = paleopixel.PaleoPixel(PALEOPIXEL_COUNT)

# Combine them into one SuperPixel strand
strand = SuperPixel(strand1, strand2)

# Intialize the SuperPixel strand (must be called once, before other
# functions, if the SuperPixel strand contains any NeoPixel sub-strands)
strand.begin()

# Set up grid segments
grid = PixelGrid(strand, (311, 10), (310, -10), (291, 10), (290, -10), (271, 10), (246, -41), (165, 41), (164, -41), (83, 41), (82, -41), (3, 39))
button_grid = PixelGrid(strand, (0, 3))
rattan_grid = PixelGrid(strand, (311, 10), (310, -10), (291, 10), (290, -10), (271, 10))
shelf_back_grid = PixelGrid(strand, (165, 41), (83, 41), (3, 39))
shelf_front_grid = PixelGrid(strand, (246, -41), (164, -41), (82, -41))
ring_grid = PixelGrid (strand, (247, 24))

# Make these globals so threaded button functions can address it
global WHITE_TIMEOUT
WHITE_TIMEOUT = None
# Length in seconds
WHITE_TIMEOUT_LENGTH = 300

global IS_TOGGLE
IS_TOGGLE = False


# FIXME: animation functions need to know when another function has been called
#        and cancel any further animation in the current function.

# TODO: smooth transitions between animation functions

# Set up our GPIO callbacks
def button_white(channel='default'):
    """Turns on the bottom row of LEDs white, for mixing drinks.
    
    Times out based on the value in WHITE_TIMEOUT_LENGTH (seconds)
    """
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()
    print("button_white")
    print("channel: ", channel)
    GPIO.output(FISH_FLOAT, GPIO.HIGH)
    button_grid.setRowColorRGB(0, 16, 16, 16)
    button_grid.setPixelColorRGB(WHITE_LED, 0, 64, 64, 64)
    button_grid.show()
    ring_grid.setRowColorRGB(0, 0, 0, 0)
    ring_grid.show()
    shelf_back_grid.setRowColorRGB(2, 255, 160, 64) # a more "natural" white
    shelf_back_grid.show()
    WHITE_TIMEOUT = threading.Timer(WHITE_TIMEOUT_LENGTH, button_amber, ['WHITE_TIMEOUT'])
    WHITE_TIMEOUT.start()

def button_amber(channel='default'):
    """Default idle mode.
    
    TODO: subtle animation
    """
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()
    print("button_amber")
    print("channel: ", channel)
    GPIO.output(FISH_FLOAT, GPIO.HIGH)
    button_grid.setRowColorRGB(0, 16, 16, 16)
    button_grid.setPixelColorRGB(AMBER_LED, 0, 64, 64, 64)
    button_grid.show()
    ring_grid.setRowColorRGB(0, 0, 0, 0)
    ring_grid.show()
    rattan_grid.setRowColorRGB(0, 250, 127, 0)
    rattan_grid.setRowColorRGB(1, 128, 50, 0)
    rattan_grid.setRowColorRGB(2, 64, 10, 0)
    rattan_grid.setRowColorRGB(3, 0, 90, 75)
    rattan_grid.setRowColorRGB(4, 0, 0, 100)
    shelf_back_grid.setAllColorRGB(0, 2, 4)
    shelf_front_grid.setAllColorRGB(50, 20, 10)
    rattan_grid.show()
    shelf_back_grid.show()
    shelf_front_grid.show()

def toggle_red_on(channel='default'):
    """Volcano Safety Toggle: ON
    
    When on, volcano show can be started by pressing red button.
    """
    print("toggle_red_on")
    print("channel: ", channel)
    global IS_TOGGLE
    IS_TOGGLE = True
    GPIO.remove_event_detect(TOGGLE_RED_IN)
    GPIO.add_event_detect(TOGGLE_RED_IN, GPIO.FALLING, callback=toggle_red_off, bouncetime=300)

def toggle_red_off(channel='default'):
    """Volcano Safety Toggle: OFF
    
    When off, volcano show cannot be started.
    """
    print("toggle_red_off")
    print("channel: ", channel)
    global IS_TOGGLE
    IS_TOGGLE = False
    GPIO.remove_event_detect(TOGGLE_RED_IN)
    GPIO.add_event_detect(TOGGLE_RED_IN, GPIO.RISING, callback=toggle_red_on, bouncetime=300)

def button_red(channel='default'):
    """Volcano Show
    
    Requires Volcano Safety Toggle to be on.
    Starts a synchronized light, sound, and smoke show.
    TODO: final lighting sequence
    TODO: Sound
    TODO: Smoke
    """
    print("button_red")
    print("channel: ", channel)
    # Does nothing unless the toggle is on
    global IS_TOGGLE
    print("IS_TOGGLE: ", IS_TOGGLE)
    if (IS_TOGGLE):
        # Clear any timeout, so it doesn't interrupt the show
        global WHITE_TIMEOUT
        if (WHITE_TIMEOUT is not None):
            WHITE_TIMEOUT.cancel()
        # This (should) prevent another volcano run
        #     until the toggle is physically cycled first
        #     without turning off FISH_FLOAT
        IS_TOGGLE = False
        # Start the show
        button_grid.setRowColorRGB(0, 16, 16, 16)
        button_grid.setPixelColorRGB(RED_LED, 0, 64, 64, 64)
        button_grid.show()
        # Blackout
        grid.setAllColorRGB(0, 0, 0)
        grid.show()
        GPIO.output(FISH_FLOAT, GPIO.LOW)
        time.sleep(1)
        # Highlight the volcano
        y = 0  # top row
        shelf_front_grid.setAllColorRGB(0, 0, 0)
        shelf_front_grid.setPixelColorRGB(20, y, 255, 0, 0)
        shelf_front_grid.show()
        shelf_back_grid.setRowColorRGB(0, 4, 0, 0)
        shelf_back_grid.show()
        time.sleep(0.01)
        shelf_front_grid.setPixelColorRGB(19, y, 125, 0, 0)
        shelf_front_grid.setPixelColorRGB(21, y, 128, 0, 0)
        shelf_front_grid.show()
        shelf_back_grid.setRowColorRGB(0, 16, 0, 0)
        shelf_back_grid.setRowColorRGB(1, 4, 0, 0)
        shelf_back_grid.show()
        time.sleep(0.01)
        shelf_front_grid.setPixelColorRGB(18, y, 64, 0, 0)
        shelf_front_grid.setPixelColorRGB(22, y, 64, 0, 0)
        shelf_front_grid.show()
        shelf_back_grid.setRowColorRGB(0, 64, 0, 0)
        shelf_back_grid.setRowColorRGB(1, 16, 0, 0)
        shelf_back_grid.setRowColorRGB(2, 4, 0, 0)
        shelf_back_grid.show()
        time.sleep(5)
        ring_grid.setRowColorRGB(0, 255, 0, 0)
        ring_grid.show()
        time.sleep(5)
        # Play animation
        test_animation = PixelPlayer(rattan_grid, 'animation/rgb-test-16x16-lossless.mov')
        test_animation.play()
        # Blackout
        grid.setAllColorRGB(0, 0, 0)
        grid.show()
        time.sleep(1)
        # Back to idle
        button_amber(channel = 'volcano_end')


# Initialize physical button interrupts
GPIO.add_event_detect(TOGGLE_RED_IN, GPIO.RISING, callback=toggle_red_on, bouncetime=500)
GPIO.add_event_detect(BUTTON_WHITE_IN, GPIO.FALLING, callback=button_white, bouncetime=500)
GPIO.add_event_detect(BUTTON_AMBER_IN, GPIO.FALLING, callback=button_amber, bouncetime=500)
GPIO.add_event_detect(BUTTON_RED_IN, GPIO.FALLING, callback=button_red, bouncetime=500)


# Display the default pattern once
button_amber()

# Idle loop
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nAttempting to clean up…")
finally:
    GPIO.cleanup()
