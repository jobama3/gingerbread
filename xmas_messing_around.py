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
    print "   [optional] --emulate --silent --debug --delay <delayInMS> --ip <fcserverIP> --start_time <audioStartInSec>"
####################################################################

# fadecandy constants
numLEDs = 50
# If you add/remove colors, please add/remove a sequence accordingly to test_sequence.txt
rgb_colors = {
    "BLACK": (0, 0, 0),
    "WHITE": (255, 255, 255),
    "GREEN": (255, 0, 0),
    "RED": (0, 255, 0)
}
black_pixels = [(0, 0, 0)] * numLEDs

# pixel location constants
# If you add/remove locations, please add/remove a sequence accordingly to test_sequence.txt
all_pixels = range(0, numLEDs)
location_pixel_sets = {
    "ALL": all_pixels,
    "HEATHER": range(0, numLEDs / 2),
    "JOE": range(numLEDs / 2, numLEDs),
    "T": range(1, 10)
}

# argument options
emulate = False
silent = False
debug = False
audio_start_time = 0
delayMs = 0
fcServerIp = 'localhost'

# parse and validate args
try:
    opts, args = getopt.getopt(sys.argv[1:], "hds:a:eq",
                               ["help", "sequence=", "audio=", "delay=", "start_time=", "ip=", "emulate", "silent", "debug"])
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
    elif opt in ("--ip") and arg:
        fcServerIp = arg
        print "FC Server IP ", fcServerIp
    elif opt == "--start_time" and arg:
        audio_start_time = float(arg)
        print "Starting at second:", audio_start_time
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
    global emulate, running, pixels
    running = True
    
    # zero out in-memory pixel map
    pixels = [rgb_colors["BLACK"]] * numLEDs

    # create client for fadecandy
    if not emulate:
        global client
        client = opc.Client(fcServerIp + ':7890')
        if client.can_connect():
            print "Connected to fadecandy server"
        else:
            print "WARNING: Could not connect to fadecandy server, running in emulation mode."
            emulate = True

    if emulate:
        heathercandy_emulator.initialize(numLEDs, main_func, quit_func)
        sys.exit(0)

    # turn off all pixels to start
    put_pixels(black_pixels, fade=False);
    main_func()
###################################################################


####################################################################
# Handle closing all resources
def quit_func():
    global running
    running = False
    
    # turn off all pixels to end
    put_pixels(black_pixels, fade=False);
    
    if emulate:
        heathercandy_emulator.quit()
    if not silent:
        pygame.mixer.music.stop()
    
    sys.exit(0)
#####################################################################


#####################################################################
# Open the input sequnce file and read/parse it
def getmusicsequence():
    with open(sequence_file, 'r') as f:
        seq_data = f.readlines()
        for i in range(len(seq_data)):
            seq_data[i] = seq_data[i].rstrip()
    return seq_data
####################################################################


#####################################################################
# Open the input sequnce file and read/parse it
def startaudio(audio_start_time):
    if not silent:
        # Load and play the music
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play(start=audio_start_time)
####################################################################


#####################################################################
def put_pixels(pixel_def, fade=False, fade_filter=None):
    output_pixels = list(pixel_def)
    if fade_filter:
        if debug:
            print pixel_def
            print fade_filter
        for i in range(len(pixel_def)):
            (r, g, b) = pixel_def[i]
            (h, s, v) = colorsys.rgb_to_hsv(float(r) / 255, float(g) / 255, float(b) / 255)
            (r, g, b) = colorsys.hsv_to_rgb(h, s, v * fade_filter[i])
            output_pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
    if emulate:
        heathercandy_emulator.put_pixels(output_pixels)
    else:
        client.put_pixels(output_pixels)
        if not fade:
            client.put_pixels(output_pixels)
####################################################################

#####################################################################
# Get location pixel set from string
def get_location_pixels(locationstring):
    # Eventually let individual pixels or a range or a list get used
    return all_pixels if not locationstring in location_pixel_sets else location_pixel_sets[locationstring]

#####################################################################


#####################################################################
# Parse rgb value from string
def get_rgb(colorstring):
    # Use known colors, or raw values like 'rbg.255.255.255'
    multi_values = colorstring.split(".")
    if len(multi_values) == 1:
        return rgb_colors[colorstring] if colorstring in rgb_colors else rgb_colors["WHITE"]
    elif multi_values[0] == "rgb" and len(multi_values) == 4:
        return map(int, multi_values[1::1])
    else:
        return rgb_colors["WHITE"]
#####################################################################


#####################################################################
# Set all pixels in given set to a given color
def set_pixel_rgb(rgb, pixel_set):
    for i in pixel_set:
        pixels[i] = rgb
#####################################################################


class Command(object):
    def __init__(self, name, command_time, location_pixels, command_options):
        """Create a Command object
        """
        self.name = name
        self.command_time = command_time
        self.location_pixels = location_pixels
        self.command_options = command_options

    #####################################################################
    # Perform the command on global pixels
    def run(self):
        global pixels, commands_in_progress
        if self.name == "END":
            print("Merry Xmas! <3")
            quit_func()

        # parse command and update pixel map
        if "BACKGROUND_COLOR" in self.command_options:
            # enh, don't allow RAINBOW for now
            background_rgb = get_rgb(self.command_options["BACKGROUND_COLOR"])
            set_pixel_rgb(background_rgb, self.location_pixels)
        if self.name == "SET_PIXEL_SUBSET":
            if "PIXELS" not in self.command_options:
                print "ERROR: Expected command option 'PIXELS' was not included"
            else:
                # Pixel subsets are offsets from the listed location
                # No overflow checks, hopefully we are smart enough to pass in the right values :)
                location_offset = self.location_pixels[0]
                self.location_pixels = [x + location_offset for x in
                                        map(int, self.command_options["PIXELS"].split("."))]
                if debug:
                    print("pixel subset: ", self.location_pixels)
                self.name = "SET_PIXELS"
        if self.name == "SET_EVERY_OTHER_PIXEL":
            self.location_pixels = self.location_pixels[::2]
            self.name = "SET_PIXELS"
        if self.name == "SET_PIXELS":
            color = "BLACK" if "COLOR" not in self.command_options else self.command_options["COLOR"]
            if color == "RAINBOW":
                numPixels = len(self.location_pixels)
                for i in self.location_pixels:
                    (r, g, b) = colorsys.hsv_to_rgb(float(i) / numPixels, 1.0, 1.0)
                    pixels[i] = (int(r * 255), int(g * 255), int(b * 255))
            else:
                rgb = get_rgb(color)
                set_pixel_rgb(rgb, self.location_pixels)
        if self.name == "CHASE":
            d = collections.deque(pixels[i] for i in self.location_pixels)
            d.rotate(1)
            for i in self.location_pixels:
                pixels[i] = d[i]
        if "FADE" in self.name:
            v = 1.0
            if self.command_options["FTYPE"] == "UP": v = 0
            for i in self.location_pixels:
                fade_filter[i] = v
            if "END_TIME" in self.command_options:
                fades_in_progress.append(self)
    #############################################################

#####################################################################
# Parse a command string
def parse_command(command_string):
    next_step = command_string.split(",")
    if len(next_step) < 2 or (next_step[1] != "END" and len(next_step) < 3):
        # If next sequence is not formatted as expected, ignore
        print "Unexpected sequence format: ", next_step  # throw exception

    raw_time = re.split('\s|\t', next_step[0])
    if (debug):
        print "raw time: ", raw_time
    command_time = float(raw_time[0]) + delayMs / float(1000)
    if (debug):
        print "time: ", command_time
    name = next_step[1].rstrip()  # assuming this is cleaning up whitespace
    print(next_step)
    # Parse next sequence, expected format
    # TIME(S),COMMAND,LOCATION,OPTIONS[COLOR=RED;FADE=TRUE;BACKGROUND=NONE;etc]
    location = "" if name == "END" else next_step[2].rstrip()
    location_pixels = get_location_pixels(location)
    command_options = "NONE" if (len(next_step) < 4 or "=" not in next_step[3]) else dict(
        item.split("=") for item in next_step[3].split(";"))
    if debug:
        print("command options: ", command_options)

    return Command(name, command_time, location_pixels, command_options)
#####################################################################


#####################################################################
# Main control loop.  This is where the xmas magic happens.
def main_func():
    global running, fade_filter
    seq_data = getmusicsequence()
    
    startaudio(audio_start_time)
    
    # Start sequencing
    heatherSet = False
    joeSet = False
    start_time = time.time()
    step = 0
    command = None
    fades_in_progress = []
    fade_filter = [1.0] * numLEDs

    while running:
        time_elapsed = time.time() - start_time
    
        # Find next time to run command
        if command == None:
            # Expected format:
            # TIME(S),COMMAND...
            if seq_data[step].startswith("#") or "," not in seq_data[step]:
                # Comment line
                print seq_data[step]
                step += 1
                continue
    
            if audio_start_time > 0 and command_time < audio_start_time:
                step +=1
                continue
    
            command = parse_command(seq_data[step])
    
        # time to run the command!
        if command.command_time <= time_elapsed:
            command.run()
            # push pixels
            put_pixels(pixels, fade="FADE" in command.command_options, fade_filter=fade_filter)
            command = None
            step += 1
    
        else:
            for fade_command in fades_in_progress:
                end_time = float(fade_command.command_options["END_TIME"])
                if time_elapsed > end_time:
                    fades_in_progress.remove(fade_command)
                else:
                    progress = (time_elapsed - fade_command.command_time) / (end_time - fade_command.command_time)
                    if fade_command.command_options["FTYPE"] == "DOWN": progress = 1.0 - progress
                    for i in fade_command.location_pixels:
                        fade_filter[i] = progress
                    put_pixels(pixels, fade_filter=fade_filter)
#####################################################################

initialize()