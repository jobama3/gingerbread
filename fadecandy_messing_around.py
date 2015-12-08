#!/usr/bin/env python

import opc, time, random

numStrings = 1
client = opc.Client('localhost:7890')

string = [ (128, 128, 128) ] * 64
for i in range(64):
	string[i] = (random.randint(0,250), 255, random.randint(0,250))

# Immediately display new frame
pixels = string * numStrings
client.put_pixels(pixels)
client.put_pixels(pixels)

print("I did it!")
