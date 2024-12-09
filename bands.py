# bands.py
#
# A script to extract data from hyperspectral images and provide information
# about the wavelengths of bands.
#
# Simon Parsons
# September 2024
#
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
    print("bands.py expects to be run in the following modes:")
    print("1) python bands.py -h or python bands.py --Help, which displays this message.")
    print("2) python bands.py -p <filename>, or python bands.py --Print  <filename> which prints the bands in  <filename>.")
    print("3) python bands.py -f <wavelength> <filename> or python bands.py -Find <wavelength> <filename>, which prints the band corresponding to <wavelength>.")
    print("In all cases <filename> should be a hyperspectral image header file.")



def main():
    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # We support help, print(ing) bands, and the find option which
    # gives the band with a specific wavelength.
    options = "hfp:"

    # Long options
    long_options = ["Help", "Find", "Print"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)
    
        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                displayHelp()
            
            elif currentArgument in ("-f", "--Find"):
                utils.findBand(argList[-1], values[0])
            
            elif currentArgument in ("-p", "--Print"):
                utils.printBands(argList[-1])
            
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == "__main__":
    main()
