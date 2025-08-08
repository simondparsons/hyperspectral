# select.py
#
# My version of the RoI selection code from Achyut Paudel via:
# https://medium.com/@achyutpaudel50/hyperspectral-image-processing-in-python-custom-roi-selection-with-mouse-78fbaf7520aa
#
# re-written to satisfy my coding quirks and to do more exactly what I wanted.
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

# Using mouse clicks requires we use a global variable. 
# The [x, y] for each right-click event will be stored here
right_clicks =[]

# Mouse callback
#
# This function will be called whenever the mouse is right-clicked
def mouse_callback(event, x, y, flags, params):
    
    #right-click event value is 2
    if event == 2:
        global right_clicks
        
        #store the coordinates of the right-click event
        right_clicks.append([x, y])

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

# Load data
#
# We need three different images: raw data (raw reflectance values),
# white_ref- (reflectance from a white surface) and dark_ref
# (reflectance from dark, usually zeros).

# Would calibrate using:
#  Corrected Image = {RawReflectance - DarkReflectance}/ {WhiteReflectance - DarkReflectance}

# This is how we open a file:
#data_ref = envi.open('raw-data-240924/linseed_a_24_09_24.hdr','raw-data-240924/linseed_a_24_09_24.dat')
data_ref = envi.open('../data/raw-data-240703/linseed_1_a.hdr','../data/raw-data-240703/linseed_1_a.dat')
bands = data_ref.bands.centers
raw_data = np.array(data_ref.load())

# If we had the white and dark data, we would then do:
#corrected_data = np.divide(np.subtract(raw_data, dark_data), np.subtract(white_data, dark_data))

#Get RGB Image
# default
img = get_rgb(raw_data)
# based on B=465, G=532, R=630
img = get_rgb(raw_data, bands=(116,67,33))
# based on B=510, G=565.5, R=600
#img = get_rgb(raw_data, bands=(100,83,55))
#img = get_rgb(raw_data)
#img2 = get_rgb(raw_data, bands=(0,1,2))


#Select single band
#sel = 70
#img = data_ref[:,:,sel]

image = cv2.normalize(img, None, alpha = 0, beta = 255, norm_type = cv2.NORM_MINMAX, dtype = cv2.CV_32F)
image = image.astype(np.uint8)
img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#Uncomment to view the RGB Image

#cv2.namedWindow("main", cv2.WINDOW_NORMAL)
#cv2.imshow('main', img_rgb)
#cv2.imshow('main', img2)
#cv2.waitKey(0)
#cv2.destroyAllWindows()



# Now view the RGB image and mouse click to pick up some areas of the image.

cv2.namedWindow("Select the regions", cv2.WINDOW_NORMAL)
# Set mouse callback function for window
cv2.setMouseCallback('Select the regions', mouse_callback)
#image = cv2.rotate(image,cv2.ROTATE_90_CLOCKWISE)
cv2.imshow('Select the regions', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(right_clicks)

# Having collected the right clicks, extract data from around those
# points.

coordinates = right_clicks
rois = [] # returned RoIs
length = 1 # width and height
intensity = 1 # bounding box line intensity
line = 1 # bounding box line width
bounding_boxed = raw_data
cd = []
for coordinate in coordinates:
    (x, y) = coordinate
    x1 = y
    y1 = image.shape[1]-x
    (roi, bounding_boxed) = extract_roi(
        bounding_boxed, x1, y1, length, length, intensity, line)
    rois.append(roi)

print(rois)

# Now compute average reflectance over the RoIs.

int_m = []
for i in range(len(rois)):
    roi = rois[i]
    intensity = []
    for b in range(roi.shape[2]):
        intensity.append(np.mean(roi[:, :, b]))
    int_m.append(intensity)
    int_m_1 = np.array(int_m)
    int_m_1 = np.mean(int_m,axis=0)
    
print(intensity)
print(int_m_1)

# Show RoIs on a binary version of the image.

cv2.namedWindow("main", cv2.WINDOW_NORMAL)
image_sel = bounding_boxed[:,:,70]
#image_sel = cv2.rotate(image_sel,cv2.cv2.ROTATE_90_CLOCKWISE)
cv2.imshow('main', image_sel)
cv2.waitKey(0)

exit()

# The code below here is supposed to displace the spectrum, but
# crashes in my environment.

plt.figure(3)
plt.plot(bands, int_m_1, label='Mean Reflectance')

plt.legend(loc='upper left')
plt.title('Leaf Spectral Footprint\\n Mean in ROI Area')
plt.xlabel('Wavelength (nm)')
plt.ylabel('Reflectance')
plt.show()
