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
    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # We support help, convert and output
    options = "hco:"

    # Long options
    long_options = ["Help", "Convert", "Output"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)
    
        # checking each argument. Note that the -o option does not
        # currently work. The structure below works for arguments that
        # are alternatives, so doesn't allow -c to be used both on its
        # own and with another flag to set the output file.
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                displayHelp()
            
            elif currentArgument in ("-c", "--Convert"):
               fileName = argList[-1]
               adjustedImage = utils.gainAdjustFile(fileName)
               
               if currentArgument in ("-o", "--Output"):
                   outName = argList[-1]
                   utils.outputFile(outName, adjustedImage)
               else:
                   utils.outputFile(fileName[:-4] + '-gain-adjusted.hdr', adjustedImage)

                   
                # Need things here!!!
            
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == "__main__":
    main()
