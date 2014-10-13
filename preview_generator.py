#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
  elphel-preview-generator - Elphel panorama preview generator

  Copyright (c) 2014 FOXEL SA - http://foxel.ch
  Please read <http://foxel.ch/license> for more information.


  Author(s):

       Kevin Velickovic <k.velickovic@foxel.ch>


  This file is part of the FOXEL project <http://foxel.ch>.

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.


  Additional Terms:

       You are required to preserve legal notices and author attributions in
       that material or in the Appropriate Legal Notices displayed by works
       containing it.

       You are required to attribute the work as explained in the "Usage and
       Attribution" section of <http://foxel.ch/license>.
"""

# Imports
import getopt
import glob
import os
import signal
import sys

from datetime import datetime

# Global variables
NO_COLORS = 0

# Function to catch CTRL-C
def signal_handler(_signal, _frame):
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Function to check presence of an executable in PATH
def which(program):

    # Check if file is executable
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    # Split path
    fpath, fname = os.path.split(program)

    # Check if file exists
    if fpath:

        # Check if file exists
        if is_exe(program):
            return program
    else:

        # Walk over PATHS to check if file exists
        for path in os.environ["PATH"].split(os.pathsep):

            # Remove quotes from path
            path = path.strip('"')

            # Build file name
            exe_file = os.path.join(path, program)

            # Check if file exists
            if is_exe(exe_file):
                return exe_file

    # Return result
    return None

# Function to print debug messages
def ShowMessage(Message, Type=0, Halt=0):

    # Flush stdout
    sys.stdout.flush()

    # Get current date
    DateNow = datetime.now().strftime("%H:%M:%S")

    # Display proper message
    if Type == 0:
        if NO_COLORS:
            sys.stdout.write("%s [INFO] %s\n" % (DateNow, Message))
        else:
            sys.stdout.write("%s \033[32m[INFO]\033[39m %s\n" % (DateNow, Message))
    elif Type == 1:
        if NO_COLORS:
            sys.stdout.write("%s [WARNING] %s\n" % (DateNow, Message))
        else:
            sys.stdout.write("%s \033[33m[WARNING]\033[39m %s\n" % (DateNow, Message))
    elif Type == 2:
        if NO_COLORS:
            sys.stdout.write("%s [ERROR] %s\n" % (DateNow, Message))
        else:
            sys.stdout.write("%s \033[31m[ERROR]\033[39m %s\n" % (DateNow, Message))
    elif Type == 3:
        if NO_COLORS:
            sys.stdout.write("%s [DEBUG] %s\n" % (DateNow, Message))
        else:
            sys.stdout.write("%s \033[34m[DEBUG]\033[39m %s\n" % (DateNow, Message))

    # Flush stdout
    sys.stdout.flush()

    # Halt program if requested
    if Halt:
        sys.exit()

# Function to convert a JP4 file into JPEG
def JP4ToJPEG(List, _output, _temp, _grayscale=0):

    # Local counter index
    idx = 1

    # Itertate over paths
    for path in List:

        # Extract filename
        FileName = os.path.splitext(os.path.basename(path))[0]

        # Debug output
        sys.stdout.flush()
        sys.stdout.write("Processing %d/%d...\r" % (idx, len(List)))
        sys.stdout.flush()

        # Check presence of grayscale option
        if _grayscale:

            # Convert image
            os.system("movie2dng --jpeg --jpeg-quality 50 --stdout %s | djpeg -fast -scale 1/8 > %s/%s.jpeg\n" % (path, _temp, FileName))

            # Rotate image
            os.system("convert -rotate 90  %s/%s.jpeg %s/%s.jpeg\n" % (_output, FileName, _output, FileName))
        else:

            # Convert image to dng
            os.system("movie2dng --dng --stdout %s > %s/%s.dng" % (path, _temp, FileName))

            # Debay dng file and convert it into jpeg
            os.system("dcraw -c %s/%s.dng | cjpeg -dct fast -quality 50 | djpeg -scale 1/10 | cjpeg > %s/%s.jpeg" % (_temp, FileName, _output, FileName))

            # Rotate image
            os.system("convert -rotate 90  %s/%s.jpeg %s/%s.jpeg\n" % (_output, FileName, _output, FileName))

            # Remove temporary dng file
            os.remove("%s/%s.dng" % (_temp, FileName))

        # Increment counter index
        idx += 1

# Function to convert a JP4 file into JPEG (parallelized)
def JP4ToJPEG_Parallel(List, _output, _temp, _grayscale=0):

    # Local command container
    Commands = ""

    # Itertate over paths
    for path in List:

        # Extract filename
        FileName = os.path.splitext(os.path.basename(path))[0]

        # Check presence of grayscale option
        if _grayscale:

            # Convert image
            Commands += ("movie2dng --jpeg --jpeg-quality 50 --stdout %s | djpeg -fast -scale 1/8 > %s/%s.jpeg && " % (path, _temp, FileName))

            # Rotate image
            Commands += ("convert -rotate 90  %s/%s.jpeg %s/%s.jpeg\n" % (_temp, FileName, _temp, FileName))
        else:

            # Convert image to dng
            Commands += ("movie2dng --dng --stdout %s > %s/%s.dng && " % (path, _temp, FileName))

            # Debay dng file and convert it into jpeg
            Commands += ("dcraw -c %s/%s.dng | cjpeg -dct fast -quality 50 | djpeg -scale 1/10 | cjpeg > %s/%s.jpeg && " % (_temp, FileName, _output, FileName))

            # Rotate image
            Commands += ("convert -rotate 90  %s/%s.jpeg %s/%s.jpeg && " % (_output, FileName, _output, FileName))

            # Remove temporary dng file
            Commands += ("rm %s/%s.dng\n" % (_temp, FileName))

    # Write command to file
    with open("%s/.JP4ToJPEG.txt" % _temp, "w") as f:
        f.write(Commands)

    # Run GNU parallel
    os.system("cat %s/.JP4ToJPEG.txt | parallel -j+0 --eta sh -c '{}'" % _temp)

    # Remove temporary command file
    os.remove("%s/.JP4ToJPEG.txt" % _temp)

# Function to generate tiles form a crow
def MakeTiles(_input, _output):

    # Extract filename
    FileName = os.path.splitext(os.path.basename(_input))[0]

    # Split image into 3 parts
    os.system("convert -crop 33.3%%x100%% +repage %s %s/%s_%%d.jpeg" % (_input, _output, FileName))

    # Remove the unnecessary third image
    if os.path.isfile("%s/%s_3.jpeg" % (_output, FileName)):
        os.remove("%s/%s_3.jpeg" % (_output, FileName))

# Function to get a sequence of images
def getSeq(List, _sequences):

    # Local variables
    Index = 0
    Result = []

    # Iterate over file list
    for i in List:

        # Split segments of file
        parts = i.rstrip('.jpeg').split('_')

        # Compute path
        path = "%s_%s_%s_%s.jpeg " % (parts[0], parts[1], parts[2], _sequences[Index])

        # Insert into list if not present
        if not path in Result:
            Result.append(path)

        # Increment index
        Index += 1

    # Return result
    return Result

# Function to stitch a set of tiles
def StitchPano(_tilesdir, _output, _temp, _grayscale=0):

    # Retrieve file list
    List = sorted(glob.glob("%s/*_0.jpeg" % _tilesdir))

    # Check presence of grayscale option
    if _grayscale:

        # Compute crowns
        TopList = getSeq(List, [2, 2, 2, 2, 2, 2, 2, 2])
        MidList = getSeq(List, [1, 1, 1, 1, 1, 1, 1, 1])
        BotList = getSeq(List, [0, 0, 0, 0, 0, 0, 0, 0])

        # Flop images
        for i in TopList[1::2]:
            os.system("convert -flop %s %s" % (i, i))

        for i in MidList[1::2]:
            os.system("convert -flop %s %s" % (i, i))

        for i in BotList[1::2]:
            os.system("convert -flop %s %s" % (i, i))

    else:

        # Compute crowns
        TopList = getSeq(List, [2, 0, 2, 0, 2, 0, 2, 0])
        MidList = getSeq(List, [1, 1, 1, 1, 1, 1, 1, 1])
        BotList = getSeq(List, [0, 2, 0, 2, 0, 2, 0, 2])

    # Generate 3 crowns (top, middle, bottom)
    os.system("montage -mode concatenate -tile 8x %s %s/top.jpeg" % (' '.join(TopList), _temp))
    os.system("montage -mode concatenate -tile 8x %s %s/mid.jpeg" % (' '.join(MidList), _temp))
    os.system("montage -flip -mode concatenate -tile 8x %s %s/bot.jpeg" % (' '.join(BotList), _temp))

    # Stitch crowns
    os.system("convert -append %s/top.jpeg %s/mid.jpeg %s/bot.jpeg %s" % (_temp, _temp, _temp, _output))

    # Remove temporary files
    os.remove("%s/top.jpeg" % _temp)
    os.remove("%s/mid.jpeg" % _temp)
    os.remove("%s/bot.jpeg" % _temp)

# Usage display function
def _usage():
    print """
    Usage: %s [OPTIONS]

    [Required arguments]
    -i --input          Input JP4 folder
    -o --output         Output JPEG folder

    [Optional arguments]
    -h --help           Prints this
    -p --parallel       Use GNU parallel
    -g --grayscale      Write grayscale images (without debayer)

    """ % sys.argv[0]

# Program entry point function
def main(argv):

    # Arguments variables initialisation
    __Input__        = ""
    __Output__       = ""
    __Parallel__     = 0
    __GrayScale__    = 0
    __Temp__         = "/tmp/preview-generator"

    # Scope variables initialisation
    __JP4_Files__    = []
    __TimeStamps__   = []

    # Arguments parser
    try:
        opt, args = getopt.getopt(argv, "hi:o:pg", ["help", "input=", "output=", "parallel", "grayscale"])
        args = args
    except getopt.GetoptError, err:
        print str(err)
        _usage()
        sys.exit(2)
    for o, a in opt:
        if o in ("-h", "--help"):
            _usage()
            sys.exit()
        elif o in ("-i", "--input"):
            __Input__  = a.rstrip('/')
        elif o in ("-o", "--output"):
            __Output__  = a.rstrip('/')
        elif o in ("-p", "--parallel"):
            if which("parallel"):
                __Parallel__ = 1
            else:
                ShowMessage("GNU parallel not found, install it with 'sudo apt-get install parallel'", 2, 1)
        elif o in ("-g", "--grayscale"):
            __GrayScale__ = 1
        else:
            assert False, "unhandled option"

    if not __Input__ or not __Output__:
        _usage()
        sys.exit()

    # Remove previous files if exists
    if os.path.isdir(__Temp__):
        os.system("rm %s/*.jpeg" % __Temp__)
        os.system("rm %s/tiles/*.jpeg" % __Temp__)

    # Create temp folder
    os.system("mkdir -p %s/tiles" % __Temp__)

    # Retrieve list of filenames (only module 1)
    __JP4_Files__ = sorted(glob.glob("%s/*_1.jp4" % __Input__))

    # Build timestamps list
    for i in __JP4_Files__:

        # Split segments of file
        parts = os.path.basename(i).split('_')

        # Compute timestamp
        ts = "%s_%s" % (parts[0], parts[1])

        # Insert into list if not present
        if not ts in __TimeStamps__:
            __TimeStamps__.append(ts)

    # Sort timestamps
    __TimeStamps__ = sorted(__TimeStamps__)

    # Initialize counter index
    idx = 1

    # Iterate over timestamps
    for ts in __TimeStamps__:

        # Debug output
        ShowMessage("%d/%d processing %s..." % (idx, len(__TimeStamps__), ts))

        # Debug output
        ShowMessage("Converting modules to jpeg")

        # Build list of images to be converted
        JP4ToJPEG_List = []
        for i in range(1, 9):
            JP4ToJPEG_List.append("%s/%s_%d.jp4" % (__Input__, ts, i))

        # Check presence of parallel option and start conversion
        if __Parallel__:
            JP4ToJPEG_Parallel(JP4ToJPEG_List, __Temp__, __Temp__, __GrayScale__)
        else:
            JP4ToJPEG(JP4ToJPEG_List, __Temp__, __Temp__, __GrayScale__)

        # Debug output
        ShowMessage("Extracting tiles")

        # Create tiles for previously converted images
        for i in range(1, 9):
            MakeTiles("%s/%s_%d.jpeg" % (__Temp__, ts, i), "%s/tiles" % __Temp__)

        # Debug output
        ShowMessage("Stitching panorama")

        # Stitch panorama
        StitchPano("%s/tiles" % __Temp__, "%s/%s.jpeg" % (__Output__, ts), __Temp__, __GrayScale__)

        # Remove temporary files
        os.system("rm %s/*.jpeg" % __Temp__)
        os.system("rm %s/tiles/*.jpeg" % __Temp__)

        # Increment counter index
        idx += 1

# Program entry point
if __name__ == "__main__":
    main(sys.argv[1:])
