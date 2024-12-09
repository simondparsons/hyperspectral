bands.py   : looks at the bands in a hyperspectral header file, matching
             band index to frequency.

viewer.py  : generates an RGB image from a hyperspectral one. Needs the
             relevant bands as arguments.

hyper.py   : the start of tools to analyse hyperspectral images. Right
             now just computes the spectrum over the entire image, looking at
             average intensity at every wavelength.

convert.py : applies gain conversion to an image, generating a new image.

clicker.py : some code grabbed from the internet. Should allow
             selection of an roi within an image. Not clear how useful it is.

fragment.py : some stuff that may or may not be useful.

envi.py    : the original envi.py from the spectral package.

my-hacked-envi.py : as the name suggests, my mods to allow the
              extraction of gain data. TBC, I didn't change any of the
              structures, just changed what elements are read from the
              header file into the existing structure replacing some
              stuff that isn't needed for viewer.py. This might cause
              problems down the line.

TODO:
1) Since all of these scripts have common elements, a proper
re-write is needed to pull those into a utils library to reduce
duplication.

Currently converted to use utils: bands.py, viewer.py, convert.py 

2) Ultimately I want to only use the hacked verison of envi.py when gain
conversion is necessary. That is now isolated into convert.py (use
that to create a new gain-coverted image and then run everything else
on that) so we should just be able to call the modified version from
that script.