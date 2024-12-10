# convert.py
#
# A script to apply gain-conversion to a hyperspectral image.
#
# Simon Parsons
# September 2024
#
# Borrowing from:
# https://www.spectralpython.net
# https://www.geeksforgeeks.org/command-line-arguments-in-python/

# Note that if you use the default output file, this will be in the
# same directory as the script is run --- if you need to specify a
# different location, use the -o/--Output option to give the path.

import sys
import getopt
import spectral as sp
#import my_hacked_envi
import utils

#
# Print help message.
#
def displayHelp():
    print("convert.py expects to be run in the following modes:")
    print("1) python convert.py -h or python convert.py --Help, which displays this message.")
    print("2) python convert.py -c <filename>, or python convert.py --Convert  <filename> which generates a new, gain converted, file <filename>-gain-adjusted")
    print("3) python convert.py -c <filename> -o <new-name> or python convert.py --Convert <filename> ---Output <new-name> which generates a new, gain converted, file <new-name>")
    print("In all cases <filename> should be a hyperspectral image header file.")


def main():
    # Set flags
    help = False
    inputFile = False
    outputFile = False
    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # We support help, convert and output. Convert and output have
    # associated values.
    options = "hc:o:"

    # Long options. Again Convert and Output take values.
    long_options = ["Help", "Convert=", "Output="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)

        # Checking each argument. Note that currentValue is only
        # instantiated if the argument was previosuly specified to
        # take a value.
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                help = True
                displayHelp()
            
            elif currentArgument in ("-c", "--Convert"):
                inputFile = True
                fileName = currentValue
               
            elif currentArgument in ("-o", "--Output"):
                outputFile = True
                outName = currentValue

        # Now process the image so long as we have at least specified
        # an output file. If we have specified help, then we do no
        # processing.
        if (not help) and inputFile:
            adjustedImage = utils.gainAdjustFile(fileName)
            if outputFile:
                utils.outputFile(outName, adjustedImage)
            else:
                utils.outputFile(fileName[:-4] + '-gain-adjusted.hdr', adjustedImage)
           
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == "__main__":
    main()
