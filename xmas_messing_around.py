#!/usr/bin/env python
#
# Command Line usage:
#   xmas.py <input sequence> <audio file>

import sys
import time
import pygame
import random
import opc

helpstring = "xmas.py <input sequence> <audio file>"

useMS = False

#fadecandy constants
numLEDs = 50
black = [ (0,0,0) ] * numLEDs
white = [ (255,255,255) ] * numLEDs
green = [ (255,0,0) ] * numLEDs
red = [ (0,255,0) ] * numLEDs


####################################################################
# Do whatever we need to do to reset and prep the pi
def initialize():
  #create client for fadecandy
  client = opc.Client('localhost:7890')
  
  print("I'm initializing!")
  return client;
####################################################################


#####################################################################
# Open the input sequnce file and read/parse it
def getmusicsequence():
  with open(sys.argv[1],'r') as f:
    seq_data = f.readlines()
    for i in range(len(seq_data)):
      seq_data[i] = seq_data[i].rstrip()
  return seq_data
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


num_args = len(sys.argv) - 1
if num_args != 2:
  print(num_args, "args passed in, should be 2")
  print(helpstring)
  sys.exit()

client = initialize()

# Open the input sequnce file and read/parse it
seq_data = getmusicsequence()

# Initialize light states
lights = [False for i in range(8)]

# Load and play the music
pygame.mixer.init()
pygame.mixer.music.load(sys.argv[2])
pygame.mixer.music.play()

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
      client.put_pixels(red)
      print(command)
    elif command == "JOE":
      client.put_pixels(green)
      print(command)
    command = ""

