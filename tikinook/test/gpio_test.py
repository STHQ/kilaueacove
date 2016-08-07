#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
GPIO test for the Volcano Safety Toggle
in the tiki nook for Kilauea Cove.

Author: Mark Boszko (boszko+kilaueacove@gmail.com)

License:
Licensed under The MIT License (MIT). Please see LICENSE.txt for full text
of the license.
"""

import time
import RPi.GPIO as GPIO

# Identify GPIO pins

BUTTON_WHITE_IN = 23
BUTTON_AMBER_IN = 24
BUTTON_RED_IN = 25
TOGGLE_RED_IN = 16
TOGGLE_RED_LED = 20


# Set up GPIO pins

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_WHITE_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_AMBER_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RED_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TOGGLE_RED_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(TOGGLE_RED_LED, GPIO.OUT)

# Idle loop
try:
    while True:
        if GPIO.input(TOGGLE_RED_IN):   
            print "Port TOGGLE_RED_IN is 1/HIGH/True +++"  
            GPIO.output(TOGGLE_RED_LED, 1)           
        else:  
            print "Port TOGGLE_RED_IN is 0/LOW/False -"  
            GPIO.output(TOGGLE_RED_LED, 0)           
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nAttempting to clean up…")
finally:
    GPIO.cleanup()
