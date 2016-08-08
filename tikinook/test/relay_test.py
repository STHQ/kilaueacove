#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
GPIO test for relays
for the tiki nook for Kilauea Cove.

Author: Mark Boszko (boszko+kilaueacove@gmail.com)

License:
Licensed under The MIT License (MIT). Please see LICENSE.txt for full text
of the license.
"""

import time
import RPi.GPIO as GPIO

# Identify GPIO pins

TEST_PIN = 21


# Set up GPIO pins

GPIO.setmode(GPIO.BCM)

GPIO.setup(TEST_PIN, GPIO.OUT)     

# Idle loop
try:
    while True:
        GPIO.output(TEST_PIN, True)
        time.sleep(2)
        GPIO.output(TEST_PIN, False)
        time.sleep(2)
except KeyboardInterrupt:
    print("\nAttempting to clean up…")
finally:
    GPIO.cleanup()
