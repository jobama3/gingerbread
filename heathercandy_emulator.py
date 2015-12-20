#!/usr/bin/env python
#
# Emulator for fadecandy

import pygame,threading

def initialize(numPixels, main_func, quit_func):
    pygame.init()
    global screen, running
    screen = pygame.display.set_mode((numPixels*20,20))
    thread = threading.Thread(target = main_func, args = ())
    thread.start()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_func()
                thread.join()
                running = False

def quit():
    global running
    running = False    

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