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

# Necesary libraries
from spectral import imshow, get_rgb
import spectral.io.envi as envi
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import pandas as pd
import utils
import csv

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

# This grabs an area around the mouse click.
def extract_roi(arr, x, y, w, h, intensity, line):
    roi = arr[y:y+h, x:x+w, :]
    bounding_box = arr
    #THIS PART IS JUST COLORING THE BOX AROUND THE IMAGE
    bounding_box[y-line:y, x-line:x+w+line, :] = intensity 
    bounding_box[y:y+h, x-line:x, :] = intensity 
    bounding_box[y+h:y+h+line, x-line:x+w+line, :] = intensity 
    bounding_box[y:y+h, x+w:x+w+line, :] = intensity 

    return (roi, bounding_box)

# Open the file using the spectral package and extract some data.

uncorrected = envi.open('../data/raw-data-240703/linseed_4_a.hdr','../data/raw-data-240703/linseed_4_a.dat')
data_ref = envi.open('../data/raw-data-240703/linseed_4_a-gain-adjusted.hdr','../data/raw-data-240703/linseed_4_a-gain-adjusted.dat')
bands = uncorrected.bands.centers #data_ref.bands.centers       # List of bands
raw_data = np.array(data_ref.load()) # The raw image data

#Get an RGB image which we will use to make our selections on. We use
# the default bands.
rgbImage = get_rgb(raw_data)

# Now view the RGB image, and set our mouse_callback function to
# record mouse clicks on the image.
cv2.namedWindow("Pick your points", cv2.WINDOW_NORMAL)
# Set mouse callback function for window
cv2.setMouseCallback("Pick your points", mouse_callback)
cv2.imshow("Pick your points", rgbImage)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(mouse_clicks)

# Now extract the reflectance at each point.

intensities = []
for click in mouse_clicks:
    (x, y) = click
    intensities.append(raw_data[x, y])

print(intensities)
print(bands)
# Write the set of intensities to a CSV file
# Borrowing from: https://docs.python.org/3/library/csv.html
#
with open('output.csv', 'w', newline='') as csvfile:
    iWriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    iWriter.writerow(bands)
    for intensity in intensities:
        iWriter.writerow(intensity)

# plotter.py can be used to read  this file and plot the waveforms.
