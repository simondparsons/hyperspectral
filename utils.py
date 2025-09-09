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
# https://medium.com/@achyutpaudel50/hyperspectral-image-processing-in-python-custom-roi-selection-with-mouse-78fbaf7520aa

import spectral as sp
import numpy as np
import cv2
import csv
import matplotlib.pyplot as plt

# Functions are grouped somewhat thematically until I can come up with
# a better way to do it.

#
# Mouse handling
#

# Using mouse clicks requires we use a global variable. The [x, y]
# for each left-click event will be stored here
mouse_clicks =[]

# Mouse callback
#
# This function will be called at every mouse event. We want to just
# log left click locations.
def mouse_callback(event, x, y, flags, params):
    
    #the left-click event value is 1
    if event == 1:
        global mouse_clicks        
        #store the coordinates of the left-click event
        mouse_clicks.append([x, y])

#
# Handling bands
#

# Print the band frequencies from file along with the index. 
def printBands(file):
    img = getImage(file)
    # The bands member of the SpyFile object returned by getImage() is
    # a BandInfo object that holds band information.
    bands = img.bands
    for i in range(len(bands.centers)):
        print("[",bands.centers[i], i, "]")

# Search through wavelengths until the specified one is found. Show index.
# All the key operations are provided by the spectral package.
#
# Re-written (August 2025) so that the main functionality can be accessed
# on its own.
def findBand(file, wavelength):
    wave = float(wavelength)
    img = getImage(file)
    bands = img.bands.centers

    index = locateBandsinImage(bands, wave)

    if index != -1:
        print("[",bands[index], index, "]")

    else:
        print("Wavelength not found in file")
    
    # Step through bands until the centre wavelength is no less than
    # the one we are looking for. Exploits the fact that wavelengths
    # are stored in ascending order.
    #
    # I hate jumping out of a for loop, but the while alternative was
    # even less elegant.
    #for i in range(len(bands.centers)):
        # We have counted up so that the centre of the current band is
        # no less than the wavelength.
    #    if(wave <= bands.centers[i]):
    #        print("[",bands.centers[i], i, "]")
    #        return
    # We got to the end and didn't find what we were looking for.
    #print("Wavelength not found in file")

def locateBandsinImage(bands, wavelength):
    # Step through bands until the centre wavelength is no less than
    # the one we are looking for. Exploits the fact that wavelengths
    # are stored in ascending order.
    #
    # I hate jumping out of a for loop, but the while alternative was
    # even less elegant.
    for i in range(len(bands)):
        # We have counted up so that the centre of the current band is
        # no less than the wavelength.
        if(wavelength <= bands[i]):
            return i
    # We got to the end and didn't find what we were looking for.
    return -1

# Extract the specified wavebands from a file. The expected use of
# this is to to create an RGB image, hence the name.
def showRGBImage(file, bands):
    # load image from file and grab the relevant wavelengths
    image = getImage(file)
    rgbImage = sp.get_rgb(image, bands=(int(bands[0]), int(bands[1]), int(bands[2])))
    # Use OpenCV to display the image. Click on the window when done.
    cv2.namedWindow("main", cv2.WINDOW_NORMAL)
    cv2.imshow('main', rgbImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# As above, but makes use of get_rgb's ability to infer (or at least
# guess) the rigt wavebands.
def showDefaultRGBImage(file):
    # load image from file and grab the relevant wavelengths
    image = getImage(file)
    rgbImage = sp.get_rgb(image)
    # Use OpenCV to display the image. Click on the window when done.
    cv2.namedWindow("main", cv2.WINDOW_NORMAL)
    cv2.imshow('main', rgbImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#
# Handling files
#

# Use the spectral package to create a file object (data isn't loaded
# until it is accessed.
def getImage(file):
    return sp.open_image(file)

# Use the spectral package to create a new data and header file for
# the data in the image. It will use the given name.
#
# Note that for now this only uses the default (.img) extension for
# the data file.
def outputFile(name, image, **kwargs):
    if kwargs:
        for k, val in kwargs.items():
            if k == 'ext':
                sp.envi.save_image(name, image, ext=val, dtype=np.float32)
    else:
        sp.envi.save_image(name, image, dtype=np.float32)

# Open a CSV file of waveforms and extract the set of bands and intensities
def openWavebandFile(file):
    # Read all the lines into intensities
    with open(file, 'r', newline='') as csvfile:
        iRead = csv.reader(csvfile, delimiter=',',
                            quotechar='|')
        intensities = []
        for row in iRead:
            fRow = []
            for intensity in row:
                fRow.append(float(intensity))
            intensities.append(fRow)

    # The first element is actually the list of bands
    bands = intensities.pop(0)

    return bands, intensities

# Output a CSV file of waveforms. The first line are the bands, and
# the rest of the bands are reflectancies/intensities
def outputCSVFile(bands, intensities, file):
    with open(file, 'w', newline='') as csvfile:
        iWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        iWriter.writerow(bands)
        for intensity in intensities:
            iWriter.writerow(intensity)

#
# Gain adjustment
#

# Perform gain adjustment on the file. Just load the relevant image,
# extract the gain data and pass to gainAdjustImage.
#
# Note that extracting the gain requires the hacked version of envi.py
def gainAdjustFile(file):
    # load image data and extract the 
    image = getImage(file)
    gain = image.bands.bandwidths
    adjustedImage = gainAdjustImage(image, gain)

    return adjustedImage

# Perform gain adjustment on an image. Assumes we have the gain data
# already extracted.
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

#
# Sampling from an image
#

def parsePointsToPairs(intList):
    pairedList = []
    for i in range(0, len(intList) - 1, 2):
        pairedList.append([intList[i], intList[i+1]])

    return pairedList
        
# Extract samples from file at the locations defined by points. This
# pulls out all the bands. The associated function sampleImageAtBands
# accepts a list of band indices and just returns those band values
# for each point.
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

# Extract samples, as above, but just for certain bands.
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

#
# Picking points from an image
def selectPoints(file):

    image = getImage(file)
    # Get the wavelengths. If these are missing from the metadata, we
    # will substitute numbers
    bands = image.bands.centers 
    raw_data = np.array(image.load())

    #Get an RGB image which we will use to make our selections on.
    if bands:
        # Use the code for pulling band information to pick the bands if
        # they exist:
        blueBand = locateBandsinImage(bands, 510)
        greenBand = locateBandsinImage(bands, 565)
        redBand = locateBandsinImage(bands, 600)
        rgbImage = sp.get_rgb(image, bands=(redBand, greenBand, blueBand))
    else:
        # We use default bands based on B=510, G=565.5, R=600. These are
        # not perfect, but are an improvement for my images on the
        # sp.get_rgb default.
        rgbImage = sp.get_rgb(raw_data, bands=(102, 85, 55))

    # Now view the RGB image, and set our mouse_callback function to
    # record mouse clicks on the image.
    cv2.namedWindow("Pick your points", cv2.WINDOW_NORMAL)
    # Set mouse callback function for window
    cv2.setMouseCallback("Pick your points", mouse_callback)
    cv2.imshow("Pick your points", rgbImage)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Now extract the reflectance at each point.
    intensities = []
    for click in mouse_clicks:
        (x, y) = click
        intensities.append(raw_data[x, y])

    # If the bands are not in the metadata, we will just number the
    # rows so that the plotting code has what it expects.
    if not bands:
        bands = []
        for i in range(len(intensities[0])):
            bands.append(i+1)
            
    return(bands, intensities)

#
# Plotting
#

# Plot all the intensity waveforms passed to the function, cycling
# through colours as per:
# https://stackoverflow.com/questions/4971269/how-to-pick-a-new-color-for-each-plotted-line-within-a-figure
#
# Best practice is to pass information on the bands, but we allow for
# this information to not be included. 
#
def plotWaveforms(bands, intensities):
    plt.figure()
    colors = iter(plt.cm.rainbow(np.linspace(0, 1, len(intensities))))
    for intensity in intensities:
        c = next(colors)
        if bands != None:
            plt.plot(bands, intensity, color = c)
        else:
            plt.plot(intensity, color = c)
    plt.show()

# As above, but averaging the values at each waveband.
def plotAverageWaveform(bands, intensities):
    sumIntensity = [0] * len(intensities[0])
    for i in range(len(sumIntensity)):
        for j in range(len(intensities)):
            sumIntensity[i] = sumIntensity[i] + intensities[j][i]

    aveIntensity = [0] * len(intensities[0])
    for i in range(len(aveIntensity)):
        aveIntensity[i] = sumIntensity[i]/len(intensities)

    plt.figure()
    if bands != None:
        plt.plot(bands, aveIntensity, color = 'b')
    else:
        plt.plot(aveIntensity, color = 'b')
    plt.show()

# Subtracting intensities at each waveband. Makes a lot of assumptions
# about the format of the files, but does allow for no band
# information.
def plotDifference(bands1, bands2, intensities1, intensities2, useAbs):
    # Assume we don't have band information
    
    # Each intensities is a list of lists which should have one entry.
    waveLength = min(len(intensities1[0]), len(intensities2[0]))
    waveform = [0] * waveLength

    # If we are using absilute values, we just have one waveform to show.
    if useAbs:
        for i in range(len(waveform)):
            waveform[i] = abs(intensities1[0][i] - intensities2[0][i])
            
        plt.plot(waveform, color = 'b')
        plt.show()

    # If we are not using absolute values, display in two colours
    else:
        negform = [0] * waveLength
        for i in range(len(waveform)):
            difference = intensities1[0][i] - intensities2[0][i]
            if difference > 0:
                waveform[i] = difference
            else:
                negform[i] = difference

        plt.plot(waveform, color = 'b')
        plt.plot(negform, color = 'r')
        plt.show()
        

    
# Using mouse clicks requires we use a global variable. The [x, y]
# for each left-click event will be stored here
mouse_clicks =[]

# Mouse callback
#
# This function will be called at every mouse event. We want to just
# log left click locations.
#
# Left clicks are more elegant than right clicks.
def mouse_callback(event, x, y, flags, params):
    
    #the left-click event value is 1
    if event == 1:
        global mouse_clicks
        
        #store the coordinates of the left-click event
        mouse_clicks.append([x, y])
