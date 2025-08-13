# plotter.py
#
# A script to plot the hyperspectral spectrum/spectra from a specified
# .csv file.
#
# The expected file format is one row giving the band wavelengths,
# followed by one or more rows giving the reflectance at the
# wavelength of that column.
#
# Spectra extracted from some gain-adjusted images will not have
# proper wavelngths, but instead proxies which just count rows.
#
# Simon Parsons
# September 2025
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
    print("plotter.py expects to be run in the following modes:")
    print("1) python plotter.py -h or python plotter.py --Help, which displays this message;")
    print("2) python plotter.py -l <filename>, or python plotter.py -All <filename> which plots all the spectra in <filename>; or")
    print("3) python plotter.py -v <filename> or  plotter.py -Average <filename> which computes the average of all the spectra in <filename> and plots that.")
    print("In all cases <filename> should be a csv file holding waveforms.")

#
# Just reads commandline arguments. All the work is done by functions
# in utils.py
#
def main():
    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # We support help, printing all spectra, or computing and printing
    # the pointwise average of the spectra
    options = "hl:v:"

    # Long options
    long_options = ["Help", "All=", "Average="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)
    
        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                displayHelp()
            
            elif currentArgument in ("-v", "--Average"):
                bands, intensities = utils.openWavebandFile(argList[-1])
                utils.plotAverageWaveform(bands, intensities)                
            
            elif currentArgument in ("-l", "--All"):
                bands, intensities = utils.openWavebandFile(argList[-1])
                utils.plotWaveforms(bands, intensities)
            
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

if __name__ == "__main__":
    main()
