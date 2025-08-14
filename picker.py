# picker.py
#
# My version of the RoI selection code from Achyut Paudel via:
# https://medium.com/@achyutpaudel50/hyperspectral-image-processing-in-python-custom-roi-selection-with-mouse-78fbaf7520aa
#
# Re-written to satisfy my coding quirks and to do more exactly what I wanted.
#
# Simon Parsons
# University of Lincoln
# August 2025

# Borrowing from:
# https://www.spectralpython.net
# https://www.geeksforgeeks.org/working-images-python/
# https://www.geeksforgeeks.org/command-line-arguments-in-python/

import sys
import getopt
import spectral as sp
import utils

#
# Print help message.
#
def displayHelp():
    print("picker.py expects to be run in the following modes:")
    print("1) python picker.py -h or python picker.py --Help, which displays this message;")
    print("2) python plotter.py -l <filename>, or python plotter.py -All <filename> which plots all the spectra in <filename>; or")
    print("3) python plotter.py -v <filename> or  plotter.py -Average <filename> which computes the average of all the spectra in <filename> and plots that.")
    print("In all cases <filename> should be a csv file holding waveforms.")
#
# Just reads commandline arguments. All the work is done by functions
# in utils.py
#
def main():
    # Set flags
    help = False
    inputFile = False
    outputFile = False

    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # We support help, printing all spectra, or computing and printing
    # the pointwise average of the spectra
    options = "hi:o:"

    # Long options
    long_options = ["Help", "Input=", "Output="]

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
            elif currentArgument in ("-i", "--Input"):
                inputFile = True
                fileName = currentValue
          
            # Specifies the output file name. This should have a .csv
            # extensionsince it will be in CSV format.
            elif currentArgument in ("-o", "--Output"):
                outputFile = True
                outName = currentValue
                    
        # Now process the image so long as we have at least specified
        # an input file. If we have specified help, then we do no
        # processing.
        if (not help) and inputFile:

            bands, intensities = utils.selectPoints(fileName)
            
            if outputFile:
                utils.outputCSVFile(bands, intensities, outName)
            else:
                utils.outputCSVFile(bands, intensities, 'output.csv')

        else:
            print("Need to specify an input file")
            displayHelp()
            
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
          
if __name__ == "__main__":
    main()

