#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Code specific to controlling the lights and other display events
in the tiki nook for Kilauea Cove.

Author: Mark Boszko (boszko+kilaueacove@gmail.com)

License:
Licensed under The MIT License (MIT). Please see LICENSE.txt for full text
of the license.

Version History:
- 1.0.0 - 2016-05-07 - Started development
"""

import time
import RPi.GPIO as GPIO
import threading
import neopixel
import paleopixel
from superpixel import *

GPIO.setmode(GPIO.BCM)

GPIO.setup(20, GPIO.OUT)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Set up the strand

# My LED strip configurations (for test):
NEOPIXEL_COUNT   = 244   # Number of NeoPixels in the strand
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
grid = PixelGrid(strand, (284, 10), (283, -10), (264, 10), (263, -10), (244, 10), (243, -41), (162, 41), (161, -41), (80, 41), (79, -41), (0, 39))
rattan_grid = PixelGrid(strand, (284, 10), (283, -10), (264, 10), (263, -10), (244, 10))
shelf_back_grid = PixelGrid(strand, (162, 41), (80, 41), (0, 39))
shelf_front_grid = PixelGrid(strand, (243, -41), (161, -41), (79, -41))

# Make these globals so threaded button functions can address it
global WHITE_TIMEOUT
WHITE_TIMEOUT = None

global IS_TOGGLE
IS_TOGGLE = False


# FIXME: animation functions need to know when another function has been called
#        and cancel any further animation in the current function.

# Set up our GPIO callbacks
def button_white(channel='default'):
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()
    print("button_white")
    print("channel: ", channel)
    shelf_back_grid.setRowColorRGB(2, 192, 160, 128)
    shelf_back_grid.show()
    WHITE_TIMEOUT = threading.Timer(300, button_amber, ['WHITE_TIMEOUT'])
    WHITE_TIMEOUT.start()

def button_amber(channel='default'):
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()
    print("button_amber")
    print("channel: ", channel)
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
    print("toggle_red_on")
    global IS_TOGGLE
    IS_TOGGLE = True
    GPIO.output(20, GPIO.HIGH)
    GPIO.remove_event_detect(16)
    GPIO.add_event_detect(16, GPIO.RISING, callback=toggle_red_off, bouncetime=300)

def toggle_red_off(channel='default'):
    print("toggle_red_off")
    global IS_TOGGLE
    IS_TOGGLE = False
    GPIO.output(20, GPIO.LOW)
    GPIO.remove_event_detect(16)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=toggle_red_on, bouncetime=300)

def button_red(channel='default'):
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()
    global IS_TOGGLE
    print(IS_TOGGLE)
    GPIO.output(20, GPIO.HIGH)
    print("button_red")
    print("channel: ", channel)
    # Blackout
    grid.setAllColorRGB(0, 0, 0)
    grid.show()
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
    # Play animation
    test_animation = PixelPlayer(rattan_grid, 'animation/rgb-test-16x16-lossless.mov')
    test_animation.play()
    GPIO.output(20, GPIO.LOW)
    button_amber()

# Physical button interrupts
GPIO.add_event_detect(23, GPIO.FALLING, callback=button_white, bouncetime=300)
GPIO.add_event_detect(24, GPIO.FALLING, callback=button_amber, bouncetime=300)
GPIO.add_event_detect(25, GPIO.FALLING, callback=button_red, bouncetime=2000)
GPIO.add_event_detect(16, GPIO.FALLING, callback=toggle_red_on, bouncetime=300)


# Display the default pattern once
button_amber()

# Idle loop
try:
    while 1:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nAttempting to clean up…")
    GPIO.cleanup()
