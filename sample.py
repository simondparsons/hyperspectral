# sample.py
#
# A script to extract some specifici points from a hyperspectral image.
#
# Simon Parsons
# February 2025
#
# Borrowing from:
# https://www.spectralpython.net
# https://www.geeksforgeeks.org/command-line-arguments-in-python/
# https://www.geeksforgeeks.org/python-integers-string-to-integer-list/

# Note that this just prints the sample points --- you will need to
# redirect to a file if you want to capture it.

import sys
import getopt
import spectral as sp
import utils

#
# Print help message.
#
def displayHelp():
    print("sample.py expects to be run in the following modes:")
    print("1) python sample.py -h, which displays this message.")
    print("2) python sample.py -p <list of coordinate> -f  <filename>, which prints the data from  <filename> at the coordinates.")
    print("3)  python sample.py -p <list of coordinate> -f  <filename> -b <bands>, which prints the data from  <filename> at the coordinates and for the specific bands in <bands>.")
    print("In all cases <filename> should be a hyperspectral image header file.")
    print("The <list of ccordinates> are a string \"x1 y1 x2 y2 ...\" for ease of parsing from the command line.")
    print("The set of <bands> are similarly a string with the indices of the bands required.")

def main():
    # Set flags
    help = False
    gotPoints = False
    gotBands = False
    inputFile = False
# Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # We support help, points and bands and file. Convert and output have
    # associated values.
    options = "hp:b:f:"

    # Long options. Again Convert and Output take values.
    long_options = ["Help", "Points=", "Bands=", "File="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)

        # Checking each argument. Note that currentValue is only
        # instantiated if the argument was previosuly specified to
        # take a value.
        for currentArgument, currentValue in arguments:
            print(currentArgument)
            if currentArgument in ("-h", "--Help"):
                help = True
                displayHelp()
            
            elif currentArgument in ("-p", "--Points"):
                gotPoints = True
                # Convert the list of points into an array of
                # pairs of coordinates
                points = list(map(int, currentValue.split()))
                print(points)
                points = utils.parsePointsToPairs(points)

            elif currentArgument in ("-f", "--File"):
                inputFile = True
                fileName = currentValue
                print(fileName)
                
            elif currentArgument in ("-b", "--Bands"):
                gotBands = True
                bands = list(map(int, currentValue.split()))

        # Now process the image so long as we have at least specified
        # a pair of point coordinates and a file. If we have specified
        # help, then we do no processing.
        #
        # Note that there is no error checking here on the format of
        # the points and bands data.
        if (not help) and gotPoints and inputFile:
            if gotBands:
                output = utils.sampleImageAtBands(points, bands, fileName)
            else:
                output = utils.sampleImage(points, fileName)

            print(output)

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == "__main__":
    main()
    
