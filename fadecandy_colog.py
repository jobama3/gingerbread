#!/usr/bin/env python

import opc, time, sys, random, collections, colorsys

fadecandy_ip = "localhost" if sys.argv.count < 3 else sys.argv[2]
client = opc.Client(fadecandy_ip + ':7890')

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
    for i in range(start, end - 1, 2):
        pixels[i] = red
        pixels[i + 1] = green
elif color == "random":
    for i in range(start, end):
        pixels[i] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
elif color == "rainbow":
    for i in range(start, end):
        (r, g, b) = colorsys.hsv_to_rgb(float(i) / end, 1.0, 1.0)
        pixels[i] = (int(r * 255), int(g * 255), int(b * 255))

if (len(sys.argv)>2):
    action = sys.argv[2]
else:
    action = "on"
    
if action == "chase":
    d = collections.deque(pixels)
    for i in range(0, 300):
        time.sleep(0.05)
        d.rotate(1)
        client.put_pixels(d)
elif action == "fadetest":
     # Stores as HSV values, modifies V value to fade down and back, sending each frame
    hsv = [ colorsys.rgb_to_hsv(float(r)/255, float(g)/255, float(b)/255) for (r ,g, b) in pixels ]
    for j in range(0, 50):
        for i in range(start, end):
            (h, s, v) = hsv[i]
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v * (50 - j) / 50)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
        client.put_pixels(pixels)
        print pixels[0]
        time.sleep(0.05)
    for j in range(0, 50):
        for i in range(start, end):
            (h, s, v) = hsv[i]
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v * j / 50)
            pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
        client.put_pixels(pixels)
        time.sleep(0.05)
elif action == "fadetest2":
     # Demonstrates fadecandy interpolation based on time between previous frame
    blackpixels = [(0, 0, 0)] * mappedPixels
    client.put_pixels(blackpixels)
    time.sleep(0.5)
    client.put_pixels(blackpixels)
    time.sleep(0.5)
    client.put_pixels(pixels)
    time.sleep(2)
    client.put_pixels(blackpixels)
    time.sleep(5)
    client.put_pixels(pixels)
    time.sleep(5)
    client.put_pixels(blackpixels)

else:
    # Immediately display new frame
    client.put_pixels(pixels)
    client.put_pixels(pixels)
