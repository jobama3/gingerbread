#!/usr/bin/env python
#
# Command Line usage:
#   xmas.py <input sequence> <audio file>

import sys, colorsys, collections, re
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
  print "   [optional] --emulate --silent --debug --delay <delayInMS>"
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
debug = False
delayMs = 0

#parse and validate args
try:                                
  opts, args = getopt.getopt(sys.argv[1:], "hds:a:eq", ["help", "sequence=", "audio=", "delay=", "emulate", "silent", "debug"])
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
  elif opt in ("--delay") and arg:
    delayMs = int(arg)
    print "Including delay of ", delayMs
  elif opt in ("-e", "--emulate"):
    emulate = True
    print "Emulating"
  elif opt in ("-q", "--silent"):
    silent = True
  elif opt in ("-d", "--debug"):
    debug = True

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
  put_pixels(black_pixels, fade=False);
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
def put_pixels(pixels, fade=False):
  if emulate:
    heathercandy_emulator.put_pixels(pixels)
  else:
    client.put_pixels(pixels)
    if not fade:
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
  # Use known colors, or raw values like 'rbg.255.255.255'
  multi_values = colorstring.split(".")
  if len(multi_values) == 1:
    return rgb_colors[colorstring] if colorstring in rgb_colors else rgb_colors["WHITE"]
  elif multi_values[0] == "rgb" and len(multi_values) == 4:
    return (multi_values[1], multi_values[2], multi_values[3])
  else:
    return rgb_colors["WHITE"]
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
  
  # Find next time to run command
  if command == "":
    # Expected format:
    # TIME(S),COMMAND...
    if seq_data[step].startswith("#") or "," not in seq_data[step]:
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
    
    raw_time = re.split('\s|\t', next_step[0])
    if (debug):
      print "raw time: ", raw_time
    if (useMS):
      command_time = int(raw_time[0]) + delayMs
    else:
      command_time = float(raw_time[0]) + delayMs/float(1000)
    if (debug):
      print "time: ", command_time
      
    command = next_step[1].rstrip() #assuming this is cleaning up whitespace
    print(next_step)

  # time to run the command!
  if command_time <= time_elapsed:
    if command == "END":
      print("Merry Xmas! <3")
      put_pixels(black_pixels, fade=True)
      sys.exit()
    
    # Parse next sequence, expected format
    # TIME(S),COMMAND,LOCATION,OPTIONS[COLOR=RED;FADE=TRUE;BACKGROUND=NONE;etc]
    location = next_step[2].rstrip()
    location_pixels = get_location_pixels(location)
    command_options = "NONE" if (len(next_step) < 4 or "=" not in next_step[3]) else dict(item.split("=") for item in next_step[3].split(";"))
    if debug:
      print("command options: ", command_options)
    
    # parse command and update pixel map
    if "BACKGROUND_COLOR" in command_options:
      # enh, don't allow RAINBOW for now
        background_rgb = get_rgb(command_options["BACKGROUND_COLOR"])
        set_pixel_rgb(background_rgb, location_pixels)
    if command == "SET_PIXEL_SUBSET":
      if "PIXELS" not in command_options:
        print "ERROR: Expected command option 'PIXELS' was not included"
      else:
        # Pixel subsets are offsets from the listed location
        # No overflow checks, hopefully we are smart enough to pass in the right values :)
        location_offset = location_pixels[0]
        location_pixels = [x+location_offset for x in map(int, command_options["PIXELS"].split("."))]
        if debug:
          print("pixel subset: ", location_pixels)
        command = "SET_PIXELS"
    if command == "SET_EVERY_OTHER_PIXEL":
      location_pixels = location_pixels[::2]
      command = "SET_PIXELS"
    if command == "SET_PIXELS":
      color = "BLACK" if "COLOR" not in command_options else command_options["COLOR"]
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
    put_pixels(pixels, fade="FADE" in command_options)
    command = ""
    step += 1
