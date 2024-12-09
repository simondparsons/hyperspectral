# hyper.py
#
# Some basic handling of hyperspectral images using Pillow and Spectral
#
# Simon Parsons
# August 2024
#
# Borrowing from:
# https://www.spectralpython.net
# https://www.geeksforgeeks.org/working-images-python/
# https://www.geeksforgeeks.org/command-line-arguments-in-python/
# https://www.geeksforgeeks.org/python-list-files-in-a-directory/

# Needs work to allow command line arguments and to (maybe) exploit
# the name structure of the data files and/or use the os interface to
# be able to handle directory structures. This is all hardwired right
# now in "folders" and "filenames", but the rest of the code is
# flexible enough to handle any number of images (and image
# dimensions).

import sys
import getopt
import numpy as np
import spectral as sp
import matplotlib.pyplot as plt

#
# Print help message.
#
def displayHelp():
    print("hyper.py expects to be run in the following modes:")
    print("1) python hyper.py -h or python hyper.py --Help, which displays this message.")
    print("2) python hyper.py -p <frac> or python hyper.py --PCA frac, which does a PCA and then redcues to the set of eigenvalues that capture <frac> of the variataion.")
    print("3) python hyper.py -w or python hyper.py --Waveform, which computes the average intensity across the images at every wavelength.")
    
#
# Use the spectral package to create a file object (data isn't loaded
# until it is accessed. 
#
def getImage(file):
    return sp.open_image(file)

#
# Load a set of images and return them in an np array. Note that
# "images" here are data objects representing images, rather than
# images themselves.
#
# Note that this assumes that the files within each folder have the
# same name, which was true for some of the development work, but
# needs to be fixed before running this on more than one folder.
#
def loadAllImages(folders, fileNames):
    images = np.empty(shape=(len(folders), len(fileNames)), dtype='object')
    for i in range(len(folders)):
        for j in range(len(fileNames)):
            img = getImage(folders[i] + '/' + fileNames[j])
            print(img.__class__)
            print(img)
            images[i][j] = img

    # print(images)
    return images

#
# Get the pixel data from the relevant files identified by the image
# objects.  rows and columns define the size of the array holding the
# image objects, which in turn tells us how many images we are dealing
# with.
#
def extractPixelData(images):
    rows = images.shape[0]
    columns = images.shape[1]
    arrays = np.empty(shape=(rows, columns), dtype='object')
    for i in range(rows):
        for j in range(columns):
            arrays[i][j] = images[i][j].load()

    # arrays[a][b] is a single hyperspectral image with dimension
    # (arrays[a][b].shape[0], arrays[a][b].shape[1], arrays[a][b].shape[2]).
    # 
    # imageBands are the wavelengths, and at each wavelength there
    # is an array of pixels that is imageRows x imageColumns in size.
    # This is 1024 x 1024 for the camera we are using.
    #
    # A single "pixel" is a single value from the imageRows x imageColumns
    # and one of the bands. For example, we have a [0, 0] in the first and
    # (if it exists) the 200th band:
    #
    # pixel = arrays[0][0][:, :, 0][0, 0]
    # pixel = arrays[0][0][:, :, 199][0, 0]

    return arrays

def summariseImages(arrays):
    rows = arrays.shape[0]
    columns = arrays.shape[1]
    # A band is an array, the size of the images, that can be extracted from arrays as
    # follows:
    #
    # band = arrays[0][0][:, :, 0]
    #
    # We want to sum over this to get the total intensity at that
    # wavelength and then plot it as a line/signal...
    #
    # In other words, we want to summarise each image by plotting the
    # average intensity of each of the bands.
    #
    # For each image...
    allIntensities = np.empty(shape=(rows, columns), dtype='object')
    for i in range(rows):
        # ...iterate over each of the N bands, computing the average
        # intensity over the image at that wavelength. We pull the
        # dimensions of arrays from the shape sttribute.
        for j in range(columns):
            numBands = arrays[i][j].shape[2]
            # Give us some indication how we are doing
            print("[", i, ",", j, "]", end='', flush=True)
            band = []
            intensities = []
            for k in range(numBands):
                intensity = 0
                band = arrays[i][j][:, :, k]
                rows = arrays[i][j].shape[0]
                columns = arrays[i][j].shape[1]
                for l in range(rows):
                    for m in range(columns):
                        intensity += band[l,m]

                averageIntensity = (intensity/(rows * columns))[0]
                intensities.append(averageIntensity)
                allIntensities[i][j] = intensities
    print("")
    return allIntensities

#
# Having generated image summaries in terms of average intensities at
# every wavelength, plot these as a wavefom that, in some sense,
# summarises the images.
#
def plotIntensities(allIntensities):
    plt.figure()
    rows = allIntensities.shape[0]
    columns = allIntensities.shape[1]
    for i in range(rows):
        for j in range(columns):
            plt.subplot(rows, columns, (i*columns) + (1+j))
            plt.plot(allIntensities[i,j], color = 'b')
    
    plt.show()
                      
#
# Analyse intensities at different wavelengths.
#
def plotIntensityWaveforms(folders, fileNames):
    images = loadAllImages(folders, fileNames)
    arrays = extractPixelData(images)
    intensities = summariseImages(arrays)
    plotIntensities(intensities)

#
# Use the PCA code in the spectral analysis library to do a PCA.
#
def extractPComponents(images):
    rows = images.shape[0]
    columns = images.shape[1]
    pc =  np.empty(shape=(rows, columns), dtype='object')
    for i in range(rows):
        for j in range(columns):
            pc[i][j] = sp.principal_components(images[i][j])
            print(len(pc[i][j].eigenvalues))
    return pc

#
# Use the PCA code in the spectral analysis library to reduce the
# principal components to the <number> eignevalues.
#
# Could use something very simiolar to reduce the eigenvalues to a
# number that captures some set percentage of the variation (use
# reduce(fraction=<number>))
#
def reducePComponents(pc, number):
    rows = pc.shape[0]
    columns = pc.shape[1]
    pc_frac =  np.empty(shape=(rows, columns), dtype='object')
    for i in range(rows):
        for j in range(columns):
            pc_frac[i][j] = pc[i][j].reduce(num=number)
           
    return pc_frac

#
# Use the spectral library to handle the transformation of data to use
# the eigenvalues of a PC analysis.  Both pc and data have the same
# dimensions.
#
def transformData(pc, data):
    rows = pc.shape[0]
    columns = pc.shape[1]
    transformed =  np.empty(shape=(rows, columns), dtype='object')
    for i in range(rows):
        for j in range(columns):
            transformed[i][j] = pc[i][j].transform(data[i][j])
            print("Here is the transformmed image")
            print(transformed[i][j])
            
    return transformed

def outputFiles(transformed, folders, fileNames):
    for i in range(len(folders)):
        for j in range(len(fileNames)):
            newName = fileNames[j][:-4] + '-reduced.hdr'
            sp.envi.save_image(folders[i] + '/' + newName, transformed[i][j], dtype=np.float32)
    
#
# Perform a principle components analysis on the images.
#
# Not currently used (main calls these functions directly)
#
def pcAnalysis(folders, fileNames, num):
    images = loadAllImages(folders, fileNames)
    pc = extractPComponents(images)
    pc_frac = reducePComponents(pc, num)
          
def main():

    # Define which header files to use. Assumes this code is run in
    # the code directory, and the data is in the ../data directory
    # with foldernames and filenames correct.
    #
    # File numbering uses the old/original convention and relates to the
    # N treatment as so:
    # 1: 160 kg/ha
    # 2: 120 kg/ha
    # 3:  80 kg/ha
    # 4:  40 kg/ha
    # 5:   0 kg/ha
    #
    # Would be good to rewrite this to allow the files to be entered
    # as a command line arguments, preferably allowing passing a
    # directory and having the script recursively descend the
    # structure.

    folders =  ['../data/raw-data-240924']#, 'raw-data-240718' ]
    #fileNames = ['linseed_1_a.hdr', 'linseed_2_a.hdr', 'linseed_3_a.hdr', 'linseed_4_a.hdr', 'linseed_5_a.hdr']
    fileNames = ['linseed_a_24_09_24.hdr'] #, 'linseed_b_24_09_24.hdr']#, 'linseed_c_24_09_24.hdr', 'linseed_d_24_09_24.hdr', 'linseed_e_24_09_24.hdr']

    # Drop the filename from the list of command line arguments
    argList = sys.argv[1:]

    # Theoptions are help, display intensity over wavelengths and do a PCA analysis.
    options = "hwp:"

    # Long options
    long_options = ["Help", "Waveform", "PCA"]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argList, options, long_options)
        print(arguments)
        
        # checking each argument
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-h", "--Help"):
                displayHelp()
            
            elif currentArgument in ("-w", "--Waveform"):
                # Generate summary plot of intensity across wavebands.
                plotIntensityWaveforms(folders, fileNames)

            elif currentArgument in ("-p", "--PCA"):
                # Carry out a PCA analysis and write the data to files
                # (one for each input file) in the same directory. num
                # is the number of pc components to use.
                num =  int(arguments[0][1])
                images = loadAllImages(folders, fileNames)
                pc = extractPComponents(images)
                pc_frac = reducePComponents(pc, num)
                pc_transform = transformData(pc_frac, images)
                outputFiles(pc_transform, folders, fileNames)
    
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))
    exit()

if __name__ == "__main__":
    main()
