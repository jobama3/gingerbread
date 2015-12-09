#!/usr/bin/env python
#
# Command Line usage:
#   xmas.py <input sequence> <audio file>

import sys
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
black = (0,0,0)
white = (255,255,255)
green = (255,0,0)
red = (0,255,0)
black_pixels = [ black ] * numLEDs

#pixel location constants
all_pixel_set = range(0, numLEDs);
heather_pixel_set = range(0, numLEDs/2)
joe_pixel_set = range(numLEDs/2, numLEDs);

#options
emulate = False
silent = False
useMS = False

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
# Open the input sequnce file and read/parse it
def getcurtime():
  if useMS:
    cur_time = int(round(time.time()*1000))
  else:
    cur_time = time.time()
  return cur_time
#####################################################################


#####################################################################
# Set all pixels in given set to a given color
def set_pixel_rgb(rgb, pixel_set):
  for i in pixel_set:
    pixels[i] = rgb
#####################################################################


#####################################################################
# Set all pixels in given set to a given color
def get_pixel_set(set_name):
  for i in pixel_set:
    pixels[i] = rgb
#####################################################################



initialize()
seq_data = getmusicsequence()

startaudio()

# zero out in-memory pixel map
pixels = black_pixels

# Start sequencing
heatherSet = False
joeSet = False
start_time = getcurtime()
step       = 1 #ignore the header line
command = ""
while True :
  time_elapsed = getcurtime() - start_time
  
  if command == "":
    # Format of input sequence data
    # TIME(S),COMMAND,VALUE
    next_step = seq_data[step].split(",");
    
    if (useMS):
      command_time = int(next_step[0])
    else:
      command_time = float(next_step[0])
    command = next_step[1].rstrip() #assuming this is cleaning up whitespace
    value = next_step[2] if len(next_step) > 2 else "WHITE"

  # time to run the command
  if command_time <= time_elapsed:
    # print next_step
    print(command)
    step += 1
    
    # parse command and update pixel map
    if command == "END":
      sys.exit()
    elif command == "ALL":
      set_pixel_rgb(white, all_pixel_set)
    elif command == "HEATHER":
      color = red if heatherSet else white
      heatherSet = not heatherSet
      set_pixel_rgb(color, heather_pixel_set)
    elif command == "JOE":
      color = white if joeSet else green
      joeSet = not joeSet
      set_pixel_rgb(color, joe_pixel_set)
    
    # push pixels
    put_pixels(pixels)
    command = ""

