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
# same directory as the original file --- if you need to specify a
# different location, use the -o/--Output option to give the path.
#
# Note also that the gain adjusted image is currently missing the
# metadata frrom the original image. There should be a way, using the
# spectral package, to copy this over. See the use of matadata here:
#
# https://www.spectralpython.net/class_func_ref.html#spectral.io.envi.open

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
    print("4) Using -e <extension> or --Extension <extension> allows us to give an extension for the image file other than the default .img")
    print("In all cases <filename> should be a hyperspectral image header file.")
          
          
def main():
    # Set flags
    help = False
    inputFile = False
    outputFile = False
    extension = False
    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]
          
    # We support help, convert, output and extension. Convert, output
    # and extension have associated values.
    options = "hc:o:e:"
          
    # Long options. Again Convert and Output take values.
    long_options = ["Help", "Convert=", "Output=", "Extension="]
          
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)
        
        # Checking each argument. Note that currentValue is only
        # instantiated if the argument was previously specified to
        # take a value.
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                help = True
                displayHelp()
          
            # Identifies the header file of the image to convert
            elif currentArgument in ("-c", "--Convert"):
                inputFile = True
                fileName = currentValue
          
            # Specifies the output file name Must have an .hdr
            # extension. The image file defualts to .img
            elif currentArgument in ("-o", "--Output"):
                outputFile = True
                outName = currentValue
          
            # If we want to specify the extension of the image file
            elif currentArgument in ("-e", "--Extension"):
                extension = True
                extensionName = currentValue
          
            # Now process the image so long as we have at least specified
            # an input file. If we have specified help, then we do no
            # processing.
        if (not help) and inputFile:
            adjustedImage = utils.gainAdjustFile(fileName)
            if outputFile:
                if extension:
                    # Image file extension is handled by the spectral
                    # package so pass the info along.
                    utils.outputFile(outName, adjustedImage, ext=extensionName)
                else:
                    utils.outputFile(outName, adjustedImage)
            else:
                if extension:
                    utils.outputFile(fileName[:-4] + '-gain-adjusted.hdr', adjustedImage, ext=extensionName)
                else:
                    utils.outputFile(fileName[:-4] + '-gain-adjusted.hdr', adjustedImage)
                
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
          
if __name__ == "__main__":
    main()
          
