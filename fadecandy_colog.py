#!/usr/bin/env python

import opc, time, sys, random, collections, colorsys

client = opc.Client('localhost:7890')

start = 0
end = 50
mappedPixels = 50

green = (255, 128, 128)
white = (255, 255, 255)
red = (128, 255, 128)
blue = (128, 128, 255)
black = (0, 0, 0)

pixels = [(0, 0, 0)] * mappedPixels

color = sys.argv[1]
if color == "red":
    for i in range(start, end):
        pixels[i] = red
elif color == "white":
    for i in range(start, end):
        pixels[i] = white
elif color == "green":
    for i in range(start, end):
        pixels[i] = green
elif color == "blue":
    for i in range(start, end):
        pixels[i] = blue
elif color == "black":
    for i in range(start, end):
        pixels[i] = black
elif color == "redgreen":
    for j in range(0, 20):
        time.sleep(0.5)
        for i in range(start, end - 1, 2):
            pixels[i] = (red, green)[j % 2 == 0]
            pixels[i + 1] = (green, red)[j % 2 == 0]
        client.put_pixels(pixels)
elif color == "random":
    for i in range(0, 20):
        time.sleep(0.5)
        for i in range(start, end):
            pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
elif color == "rainbow":
    for i in range(start, end):
        (r, g, b) = colorsys.hsv_to_rgb(float(i) / end, 1.0, 1.0)
        pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

action = sys.argv[2]
if action == "chase":
    d = collections.deque(pixels)
    for i in range(0, 300):
        time.sleep(0.05)
        d.rotate(1)
        client.put_pixels(d)
elif action == "fadetest":
    for j in range(0, 150):
        for i in range(start, end):
            (h, s, v) = colorsys.rgb_to_hsv(pixels[i])
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v * (150 - j) / 150)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
        client.put_pixels(pixels)
    for j in range(0, 150):
        for i in range(start, end):
            (h, s, v) = colorsys.rgb_to_hsv(pixels[i])
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v * j / 150)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
        client.put_pixels(pixels)
else:
    # Immediately display new frame
    client.put_pixels(pixels)
    client.put_pixels(pixels)
