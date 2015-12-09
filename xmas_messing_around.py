#!/usr/bin/env python
#
# Command Line usage:
#   xmas.py <input sequence> <audio file>

import sys, colorsys, collections
import getopt
import time
import pygame
import random
import opc
import heathercandy_emulator

####################################################################
# Print help
def usage():
  print "xmas.py --sequence <sequence file> --audio <audio file>"
  print "   [optional] --emulate --silent"
####################################################################

#fadecandy constants
numLEDs = 50
# If you add/remove colors, please add/remove a sequence accordingly to test_sequence.txt
rgb_colors = {
  "BLACK": (0,0,0),
  "WHITE": (255,255,255),
  "GREEN": (255,0,0),
  "RED": (0,255,0)
}
black_pixels = [ (0,0,0) ] * numLEDs

#pixel location constants
# If you add/remove locations, please add/remove a sequence accordingly to test_sequence.txt
all_pixels = range(0, numLEDs)
location_pixel_sets = {
  "ALL": all_pixels,
  "HEATHER": range(0, numLEDs/2),
  "JOE": range(numLEDs/2, numLEDs)
}

# argument options
emulate = False
silent = False
useMS = False

# Sequence options
color_option = "COLOR"

#parse and validate args
try:                                
  opts, args = getopt.getopt(sys.argv[1:], "hs:a:eq", ["help", "sequence=", "audio=", "emulate", "silent"])
except getopt.GetoptError:
  print "Error parsing args"
  usage()
  sys.exit(2)

for opt, arg in opts:
  if opt in ("-h", "--help"):
    usage()
    sys.exit()
  elif opt in ("-s", "--sequence"):
    sequence_file = arg
  elif opt in ("-a", "--audio"):
    audio_file = arg
  elif opt in ("-e", "--emulate"):
    emulate = True
    print "Emulating"
  elif opt in ("-q", "--silent"):
    silent = True

try:
  print "Sequence file: ", sequence_file
  if not silent:
    print "Audio file: ", audio_file
  else:
    print "Running in silent mode"
  print
except NameError:
  usage()
  sys.exit(2)

####################################################################
# Do whatever we need to do to reset and prep the pi
def initialize():
  print("I'm initializing!")
  global emulate
  
  #create client for fadecandy
  if not emulate:
    global client
    client = opc.Client('localhost:7890')
    if client.can_connect():
      print "Connected to fadecandy server"
    else:
      print "WARNING: Could not connect to fadecandy server, running in emulation mode."
      emulate = True
  
  # turn off all pixels to start
  put_pixels(black_pixels, now=True);
####################################################################


#####################################################################
# Open the input sequnce file and read/parse it
def getmusicsequence():
  with open(sequence_file,'r') as f:
    seq_data = f.readlines()
    for i in range(len(seq_data)):
      seq_data[i] = seq_data[i].rstrip()
  return seq_data
####################################################################


#####################################################################
# Open the input sequnce file and read/parse it
def startaudio():
  if not silent:
    # Load and play the music
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
####################################################################


#####################################################################
def put_pixels(pixels, now=True):
  if emulate:
    heathercandy_emulator.put_pixels(pixels)
  else:
    client.put_pixels(pixels)
    if (now):
      client.put_pixels(pixels)
####################################################################


#####################################################################
# Open the input sequence file and read/parse it
def getcurtime():
  if useMS:
    cur_time = int(round(time.time()*1000))
  else:
    cur_time = time.time()
  return cur_time
#####################################################################


#####################################################################
# Get location pixel set from string
def get_location_pixels(locationstring):
  # Eventually let individual pixels or a range or a list get used
  return all_pixels if not location in location_pixel_sets else location_pixel_sets[location]
#####################################################################


#####################################################################
# Parse rgb value from string
def get_rgb(colorstring):
  # Eventually let raw rgb values get set or hsv or whatever format
  return rgb_colors[colorstring] if colorstring in rgb_colors else rgb_colors["WHITE"]
#####################################################################


#####################################################################
# Set all pixels in given set to a given color
def set_pixel_rgb(rgb, pixel_set):
  for i in pixel_set:
    pixels[i] = rgb
#####################################################################


initialize()
seq_data = getmusicsequence()

startaudio()

# zero out in-memory pixel map
pixels = [ rgb_colors["BLACK"] ] * numLEDs

# Start sequencing
heatherSet = False
joeSet = False
start_time = getcurtime()
step       = 0
command = ""
while True :
  time_elapsed = getcurtime() - start_time
  
  if command == "":
    # Find next command time.  Expected format:
    # TIME(S),COMMAND...
    if seq_data[step].startswith("#"):
      # Comment line
      print seq_data[step]
      step += 1
      continue
      
    next_step = seq_data[step].split(",");
    if len(next_step) < 2 or (next_step[1] != "END" and len(next_step) < 3):
      # If next sequence is not formatted as expected, ignore
      print "Unexpected sequence format: ", next_step
      step += 1
      continue
    
    command = next_step[1].rstrip() #assuming this is cleaning up whitespace
    print(next_step)
    
    if (useMS):
      command_time = int(next_step[0])
    else:
      command_time = float(next_step[0])

  # time to run the command
  if command_time <= time_elapsed:
    if command == "END":
      print("Merry Xmas! <3")
      put_pixels(black_pixels, now=False)
      sys.exit()
    
    # Parse next sequence, expected format (see top of script for possible options)
    # TIME(S),COMMAND,LOCATION,OPTIONS[COLOR=RED;FADE=TRUE;BACKGROUND=NONE;etc]
    location = next_step[2].rstrip()
    location_pixels = get_location_pixels(location)
    command_options = "NONE" if (len(next_step) < 4 or "=" not in next_step[3]) else dict(item.split("=") for item in next_step[3].split(";"))
    
    # parse command and update pixel map
    if command == "SET_EVERY_OTHER_PIXEL":
      location_pixels = location_pixels[::2]
      command = "SET_PIXELS"
    if command == "SET_PIXELS":
      color = "BLACK" if color_option not in command_options else command_options[color_option]
      if color == "RAINBOW":
        numPixels = len(location_pixels)
        for i in location_pixels:
          (r, g, b) = colorsys.hsv_to_rgb(float(i) / numPixels, 1.0, 1.0)
          pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
      else:
        rgb = get_rgb(color)
        set_pixel_rgb(rgb, location_pixels)
    if command == "CHASE":
      d = collections.deque(pixels)
      d.rotate(1)
      pixels = d
    
    # push pixels
    put_pixels(pixels)
    command = ""
    step += 1
