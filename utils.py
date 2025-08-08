# utils.py
#
# Some basic building blocks for manipulating hyperspecytral images 
#
# Simon Parsons
# November 2024
#
# Borrowing from:
# https://www.spectralpython.net
# https://www.geeksforgeeks.org/working-images-python/
# https://www.geeksforgeeks.org/command-line-arguments-in-python/

import spectral as sp
import numpy as np
import cv2
import matplotlib.pyplot as plt

#
# Print the band frequencies from file along with the index. 
#
def printBands(file):
    img = getImage(file)
    # The bands member of the SpyFile object returned by getImage() is
    # a BandInfo object that holds band information.
    bands = img.bands
    for i in range(len(bands.centers)):
        print("[",bands.centers[i], i, "]")

#
# Search through wavelengths until the specified one is found. Show index.
# All the key operations are provided by the spectral package.
#
def findBand(file, wavelength):
    wave = float(wavelength)
    img = getImage(file)
    bands = img.bands
    # Step through bands until the centre wavelength is no less than
    # the one we are looking for. Exploits the fact that wavelengths
    # are stored in ascending order.
    #
    # I hate jumping out of a for loop, but the while alternative was
    # even less elegant.
    for i in range(len(bands.centers)):
        # We have counted up so that the centre of the current band is
        # no less than the wavelength.
        if(wave <= bands.centers[i]):
            print("[",bands.centers[i], i, "]")
            return
    # We got to the end and didn;t find what we were looking for.
    print("Wavelength not found in file")

#
# Use the spectral package to create a file object (data isn't loaded
# until it is accessed.
#
def getImage(file):
    return sp.open_image(file)

#
# Use the spectral package to create a new data and header file for
# the data in the image. It will use the given name.
#
def outputFile(name, image):
    sp.envi.save_image(name, image, dtype=np.float32)

#
# Extract the specified wavebands. The expected use of this is to to
# create an RGB image, hence the name.
#
def showRGBImage(file, bands):
    # load image from file and grab the relevant wavelengths
    image = getImage(file)
    rgbImage = sp.get_rgb(image, bands=(int(bands[0]), int(bands[1]), int(bands[2])))
    # Use OpenCV to display the image. Click on the window when done.
    cv2.namedWindow("main", cv2.WINDOW_NORMAL)
    cv2.imshow('main', rgbImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#
# Perform gain adjustment on the file. Just load the relevant image,
# extract the gain data and pass to gainAdjustImage.
#
# Note that extracting the gain requires the hacked version of envi.py
#
def gainAdjustFile(file):
    # load image data and extract the 
    image = getImage(file)
    gain = image.bands.bandwidths
    adjustedImage = gainAdjustImage(image, gain)

    return adjustedImage

#
# Perform gain adjustment on an image. Assumes we have the gain data
# already extracted.
#
def gainAdjustImage(image, gain):
    # image is a "cube" of rows x columns x bands. gain is a
    # adjustment per band. We adjust for the gain across the entire
    # image.
    rows = image.shape[0]
    columns = image.shape[1]
    bands = image.shape[2]

    newImage = np.empty(shape=(rows, columns, bands), dtype='float')
    for i in range(bands):
        for j in range(rows):
                for k in range(columns):
                    newImage[j,k,i] = image[j,k,i] * gain[i]
    return newImage

def parsePointsToPairs(intList):
    pairedList = []
    for i in range(0, len(intList) - 1, 2):
        pairedList.append([intList[i], intList[i+1]])

    return pairedList
        
#
# Extract samples from file at the locations defined by points. This
# pulls out all the bands. The associated function sampleImageAtBands
# accepts a list of band indices and just returns those band values
# for each point.
#
def sampleImage(points, file):
    image = getImage(file)
    samples = []
    # points should be a list of pairs of coordinates:
    #
    # [ [x1, y1], [x2, y2], ...]
    #
    # and at each point we extract all the bands
    for i in range(len(points)):
        pointX = points[i][0]
        pointY = points[i][1]
        samples.append(image[pointX, pointY])
        
    return samples

#
# Extract samples, as above, but just for certain bands.
#
def sampleImageAtBands(points, bands, file):
    # Get a list of samples each of all the bands
    listOfFullSamples = sampleImage(points, file)
    reducedBandList = []
    for i in range(len(listOfFullSamples)):
        tempList = []
        for j in range(len(bands)):
            tempList.append(listOfFullSamples[i][bands[j]])

        reducedBandList.append(tempList)

    return reducedBandList


