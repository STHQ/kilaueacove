#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import RPi.GPIO as GPIO
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


# Set up our GPIO callbacks
def button_white(channel):
    print("button_white")
    colorWipe(strand, Color(255, 0, 0), 0)  # Red wipe

def button_amber(channel):
    print("button_amber")
    colorWipe(strand, Color(0, 255, 0), 0)  # Green wipe

def button_red(channel):
    print("button_red")
    colorWipe(strand, Color(0, 0, 255), 0)  # Blue wipe

# Physical button interrupts
GPIO.add_event_detect(23, GPIO.FALLING, callback=button_white, bouncetime=300)
GPIO.add_event_detect(24, GPIO.FALLING, callback=button_amber, bouncetime=300)
GPIO.add_event_detect(25, GPIO.FALLING, callback=button_red, bouncetime=300)


# Idle loop
while 1:
    time.sleep(1)

GPIO.cleanup()
