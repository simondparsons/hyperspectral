# viewer.py
#
# A script to display an RGB image from a hyperspectral one.
#
# Simon Parsons
# September 2024
#
# Originally based on code from Achyut Paudel via:
# https://medium.com/@achyutpaudel50/hyperspectral-image-processing-in-python-custom-roi-selection-with-mouse-78fbaf7520aa
# and then heavily rewritten. 

# Necesary libraries
import sys
import getopt
import numpy as np
import spectral as sp
import utils

#from spectral import imshow, get_rgb
#import spectral.io.envi as envi
#import matplotlib.pyplot as plt
#import matplotlib
#import cv2
#import os
#import pandas as pd

#
# Print help message.
#
def displayHelp():
    print("viewer.py expects to be run in the following modes:")
    print("1) python viewer.py -h or python viewer.py --Help, which displays this message.")
    print("2) python viewer.py -b band1 band2 band3 <filename>, or python viewer.py --Bands  band1 band2 band3 <filename> ")
    print("<filename> should be a hyperspectral image header file, and bands should be the indices of the red, green and blue bands within the hyperspectral image. This data can be found in the header file (or see the bands.py utility).")

#
# Main function starts here. I prefer to use main() to make this clear.
#
def main():
    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # Defining options. Note that the way that bands are passed is not
    # pretty (and doesn't specify that the options take values, but
    # allows for multiple values to be simply called.
    options = "hb"

    # Long options
    long_options = ["Help", "Bands"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)

        print(arguments)
        print(values)
        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                displayHelp()
            
            elif currentArgument in ("-b", "--Bands"):
                # Passing the relevant values to the function that
                # does all the work. 
                bands = values[0:3]
                print("Bands = ", bands)
                utils.showRGBImage(argList[-1], bands)
                       
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

# Ensure that the script runs properly on the command line
if __name__ == "__main__":
    main()

