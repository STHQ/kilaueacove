#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import RPi.GPIO as GPIO
from threading import Timer, Thread, Event
import neopixel
import paleopixel
from superpixel import *

GPIO.setmode(GPIO.BCM)

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


# FIXME: animation functions need to know when another function has been called
#        and cancel any further animation in the current function.

# Set up our GPIO callbacks
def button_white(channel=23):
    print("button_white")
    shelf_back_grid.setRowColorRGB(2, 128, 128, 128)
    shelf_back_grid.show()
    white_timer = Timer(10, button_amber)
    white_timer.start()

def button_amber(channel=24):
    print("button_amber")
    rattan_grid.setAllColorRGB(250, 127, 0)
    rattan_grid.setRowColorRGB(3, 0, 90, 75)
    rattan_grid.setRowColorRGB(4, 0, 0, 100)
    shelf_back_grid.setAllColorRGB(2, 4, 8)
    shelf_front_grid.setAllColorRGB(50, 20, 10)
    rattan_grid.show()
    shelf_back_grid.show()
    shelf_front_grid.show()

def button_red(channel=25):
    print("button_red")
    # Blackout
    grid.setAllColorRGB(0, 0, 0)
    grid.show()
    shelf_front_grid.setAllColorRGB(0, 0, 0)
    shelf_front_grid.show()
    time.sleep(1)
    # Highlight the volcano
    y = 0  # top row
    shelf_front_grid.setPixelColorRGB(20, y, 255, 0, 0)
    shelf_front_grid.show()
    shelf_front_grid.setPixelColorRGB(19, y, 255, 0, 0)
    shelf_front_grid.setPixelColorRGB(21, y, 255, 0, 0)
    shelf_front_grid.show()
    shelf_front_grid.setPixelColorRGB(18, y, 255, 0, 0)
    shelf_front_grid.setPixelColorRGB(22, y, 255, 0, 0)
    shelf_front_grid.show()
    shelf_back_grid.setAllColorRGB(255, 0, 0)
    shelf_back_grid.show()
    time.sleep(1)
    # Play animation
    test_animation = PixelPlayer(rattan_grid, 'animation/rgb-test-16x16-lossless.mov')
    test_animation.play()
    time.sleep(1)
    button_amber()

# Physical button interrupts
GPIO.add_event_detect(23, GPIO.FALLING, callback=button_white, bouncetime=300)
GPIO.add_event_detect(24, GPIO.FALLING, callback=button_amber, bouncetime=300)
GPIO.add_event_detect(25, GPIO.FALLING, callback=button_red, bouncetime=300)

# Display the default pattern once
button_amber()

# Idle loop
while 1:
    time.sleep(1)

GPIO.cleanup()
