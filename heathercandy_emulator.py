#!/usr/bin/env python
#
# Emulator for fadecandy

import pygame

def initialize(numPixels):
    pygame.init()
    global screen
    screen = pygame.display.set_mode((numPixels*20,20))

def put_pixels(pixels):
    i = 0
    print pixels
    print
    for rgb in pixels:
        try:
            pygame.draw.circle(screen, rgb, (i*20 + 10, 10), 10)
            i += 1
        except TypeError:
            print "ERROR: Could not display color", rgb
    pygame.display.update()