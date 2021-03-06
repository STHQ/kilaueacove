#!/usr/bin/env python3
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
- 2.0.0 - 2018-08-13 - Upgrades to show, and OSC for communication
- 0.2.0 - 2016-08-07 - Add the 3 button NeoPixels + the 24 ring NeoPixels
                       Fixed the red toggle detection + volcano show restriction
- 0.1.0 - 2016-05-07 - Started development
"""

import argparse
import numpy
import RPi.GPIO as GPIO
import time
import threading

from pythonosc import dispatcher
from pythonosc import osc_server

import neopixel
import paleopixel
from superpixel import *

# ------------------------------
# GPIO setup
# ------------------------------

# Identify GPIO pins

BUTTON_WHITE_IN = 23
BUTTON_AMBER_IN = 24
BUTTON_RED_IN = 25
TOGGLE_RED_IN = 16
SMOKE_CONTROL = 21

# Set up GPIO pins

GPIO.setmode(GPIO.BCM)

GPIO.setup(BUTTON_WHITE_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_AMBER_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_RED_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TOGGLE_RED_IN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(SMOKE_CONTROL, GPIO.OUT)

# ------------------------------
# LED setup
# ------------------------------

# Set up the super_strand

# My LED strip configurations (for test):
WHITE_LED = 0  # These are the LEDs inside the buttons
AMBER_LED = 1
RED_LED = 2
NEOPIXEL_COUNT = 271  # Number of NeoPixels in the super_strand
NEOPIXEL_PIN = 18  # GPIO pin connected to the pixels (must support PWM!)
PALEOPIXEL_COUNT = 50  # Number of PaleoPixels in the super_strand

# Create pixel strands with appropriate configuration.
neopixel_strand = neopixel.Adafruit_NeoPixel(NEOPIXEL_COUNT, NEOPIXEL_PIN)
paleopixel_strand = paleopixel.PaleoPixel(PALEOPIXEL_COUNT)

# Combine them into one SuperPixel super_strand
super_strand = SuperPixel(neopixel_strand, paleopixel_strand)

# Intialize the SuperPixel super_strand (must be called once, before other
# functions, if the SuperPixel super_strand contains any NeoPixel sub-strands)
super_strand.begin()

# Set up grid segments
grid = PixelGrid(super_strand, (311, 10), (310, -10), (291, 10), (290, -10), (271, 10), (246, -41), (165, 41), (164, -41),
                 (83, 41), (82, -41), (3, 39))
button_grid = PixelGrid(super_strand, (0, 3))
rattan_grid = PixelGrid(super_strand, (311, 10), (310, -10), (291, 10), (290, -10), (271, 10))
shelf_back_grid = PixelGrid(super_strand, (165, 41), (83, 41), (3, 39))
shelf_front_grid = PixelGrid(super_strand, (246, -41), (164, -41), (82, -41))
ring_grid = PixelGrid(super_strand, (247, 24))


# ------------------------------
# Eruption animation setup
# ------------------------------

# load the animation
volcano_animation = PixelPlayer(rattan_grid, '/home/pi/kilaueacove/tikinook/animation/volcano-v05-16x16.mov')


# ------------------------------
# Globals
# ------------------------------

# Make these globals so threaded button functions can address it
global WHITE_TIMEOUT
WHITE_TIMEOUT = None
# Length in seconds
WHITE_TIMEOUT_LENGTH = 300

global IS_TOGGLE
IS_TOGGLE = False


# ------------------------------
# Callback methods
# ------------------------------

# FIXME: animation functions need to know when another function has been called
#        and cancel any further animation in the current function.

# TODO: smooth transitions between animation functions

# Set up our GPIO callbacks
def button_white(channel='default'):
    """Turns on the bottom row of LEDs white, for mixing drinks.
    
    Times out based on the value in WHITE_TIMEOUT_LENGTH (seconds)
    """
    print("button_white()")
    print("channel: ", channel)

    # Cancel the timer for the white light
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()

    # Set all row colors the same as button_amber(), except
    # get the row underneath the bottom shelf, and show white
    button_grid.setRowColorRGB(0, 16, 16, 16)
    button_grid.setPixelColorRGB(WHITE_LED, 0, 64, 64, 64)
    button_grid.show()
    ring_grid.setRowColorRGB(0, 0, 0, 0)
    ring_grid.show()
    shelf_back_grid.setRowColorRGB(2, 255, 160, 64)  # a more "natural" white
    shelf_back_grid.show()

    # Start a timer to go back to amber after WHITE_TIMEOUT_LENGTH
    WHITE_TIMEOUT = threading.Timer(WHITE_TIMEOUT_LENGTH, button_amber, ['WHITE_TIMEOUT'])
    WHITE_TIMEOUT.start()


def button_amber(channel='default'):
    """Default idle mode.
    
    TODO: subtle animation
    """
    print("button_amber()")
    print("channel: ", channel)

    # Cancel the timer for the white light
    global WHITE_TIMEOUT
    if (WHITE_TIMEOUT is not None):
        WHITE_TIMEOUT.cancel()

    # Set pretty colors
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
    
    When off, volcano show cannot be started, unless triggered by OSC.
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
        # Cancel the timer for the white light, so it doesn't interrupt the show
        global WHITE_TIMEOUT
        if (WHITE_TIMEOUT is not None):
            WHITE_TIMEOUT.cancel()

        # This (should) prevent another volcano run
        #     until the toggle is physically cycled first
        IS_TOGGLE = False

        # Start the show; set color of control box buttons
        button_grid.setRowColorRGB(0, 16, 16, 16)
        button_grid.setPixelColorRGB(RED_LED, 0, 64, 64, 64)
        button_grid.show()

        # TODO: Slower fade out, bottom to top
        # Blackout
        # grid.setAllColorRGB(0, 0, 0)
        # grid.show()
        pixel_count = len(super_strand.getPixels())
        new_colors = numpy.zeros((pixel_count, 3), dtype=numpy.int)
        super_strand.fade_to_colors(new_colors=new_colors, seconds=3)

        # Smoke starts
        GPIO.output(SMOKE_CONTROL, GPIO.HIGH)

        # TODO, top row slower shrink in from edges, turn red
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
        time.sleep(10)

        # Turn the ring red to highlight smoke
        # TODO: make this fluctuate red/orage/yellow during eruption sequence
        ring_grid.setRowColorRGB(0, 255, 0, 0)
        ring_grid.show()
        time.sleep(4)

        # Play animation
        # FIXME: Slow this down!
        volcano_animation.play(delay=0.013)

        # Smoke off
        GPIO.output(SMOKE_CONTROL, GPIO.LOW)
        time.sleep(3)

        # Fade to black
        new_colors = numpy.zeros((pixel_count, 3), dtype=numpy.int)
        super_strand.fade_to_colors(new_colors=new_colors, seconds=1)
        time.sleep(3)

        # Fade up to Amber
        # Start with black
        amber_colors = numpy.zeros((pixel_count, 3), dtype=numpy.int)
        # Assign Amber colors
        amber_colors[WHITE_LED] = [16, 16, 16]
        amber_colors[AMBER_LED] = [64, 64, 64]
        amber_colors[RED_LED] = [16, 16, 16]
        # Ring is already black, no need to change
        for index in range(311, 321):
            # Rattan row 0
            amber_colors[index] = [250, 127, 0]
        for index in range(301, 311):
            # Rattan row 1
            amber_colors[index] = [128, 50, 0]
        for index in range(291, 301):
            # Rattan row 2
            amber_colors[index] = [64, 10, 0]
        for index in range(281, 291):
            # Rattan row 3
            amber_colors[index] = [0, 90, 75]
        for index in range(271, 281):
            # Rattan row 4
            amber_colors[index] = [0, 0, 100]
        for index in range(165, 206):
            # Shelf Back row 0
            amber_colors[index] = [0, 2, 4]
        for index in range(83, 124):
            # Shelf Back row 1
            amber_colors[index] = [0, 2, 4]
        for index in range(3, 42):
            # Shelf Back row 2
            amber_colors[index] = [0, 2, 4]
        for index in range(206, 247):
            # Shelf Front row 0
            amber_colors[index] = [50, 20, 10]
        for index in range(124, 165):
            # Shelf Front row 1
            amber_colors[index] = [50, 20, 10]
        for index in range(42, 83):
            # Shelf Front row 2
            amber_colors[index] = [50, 20, 10]

        # Fade
        super_strand.fade_to_colors(new_colors=amber_colors, seconds=2)

        # Comment out so I can examine the fade results
        button_amber(channel='volcano_end')


def erupt_handler(unused_addr, args, erupt):
    # erupt == 1.0 always, so I'm not even going to check
    print("erupt_handler()")
    print("unused_addr:", unused_addr)
    print("args:", args)
    print("erupt:", erupt)
    global IS_TOGGLE
    IS_TOGGLE = True
    button_red(channel='OSC')


# ------------------------------
# Main code
# ------------------------------

if __name__ == "__main__":
    # Set up OSC variables from command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.10.15", help="The ip to listen on")
    parser.add_argument("--port", type=int, default=8000, help="The port to listen on")
    args = parser.parse_args()

    # Initialize physical button interrupts
    GPIO.add_event_detect(TOGGLE_RED_IN, GPIO.RISING, callback=toggle_red_on, bouncetime=500)
    GPIO.add_event_detect(BUTTON_WHITE_IN, GPIO.FALLING, callback=button_white, bouncetime=500)
    GPIO.add_event_detect(BUTTON_AMBER_IN, GPIO.FALLING, callback=button_amber, bouncetime=500)
    GPIO.add_event_detect(BUTTON_RED_IN, GPIO.FALLING, callback=button_red, bouncetime=500)

    # Display the default pattern once
    button_amber()

    # Set up the OSC listener
    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/erupt", erupt_handler, "Erupt")
    # Run the server on its own thread
    server = osc_server.ForkingOSCUDPServer((args.ip, args.port), dispatcher)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    print("OSC listening on {}".format(server.server_address))

    # Idle loop
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nAttempting to clean up…")
    finally:
        server.shutdown()
        GPIO.cleanup()
