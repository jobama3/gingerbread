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
black = [ (0,0,0) ] * numLEDs
white = [ (255,255,255) ] * numLEDs
green = [ (255,0,0) ] * numLEDs
red = [ (0,255,0) ] * numLEDs

#parse and validate args
emulate = False
silent = False
useMS = False

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
  
  #create client for fadecandy
  if not emulate:
    global client
    global emulate
    client = opc.Client('localhost:7890')
    if client.can_connect():
      print "Connected to fadecandy server"
    else:
      print "WARNING: Could not connect to fadecandy server, running in emulation mode."
      emulate = True
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
# Open the input sequnce file and read/parse it
def put_pixels(pixels):
  if emulate:
    heathercandy_emulator.put_pixels(pixels)
  else:
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
####################################################################


initialize()
seq_data = getmusicsequence()

startaudio()

# Start sequencing
start_time = getcurtime()
step       = 1 #ignore the header line
command = "" 
while True :
  time_elapsed = getcurtime() - start_time
  
  if command == "":
    # Format of input sequence data
    # TIME(MS),COMMAND,VALUE
    next_step = seq_data[step].split(",");
    
    if (useMS):
      command_time = int(next_step[0])
    else:
      command_time = float(next_step[0])
    command = next_step[1].rstrip() #assuming this is cleaning up whitespace
    # value = next_step[2]

  # time to run the command
  if command_time <= time_elapsed:
    # print next_step
    step += 1
    if command == "END":
      sys.exit()
    elif command == "HEATHER":
      put_pixels(red)
      print(command)
    elif command == "JOE":
      put_pixels(green)
      print(command)
    command = ""

