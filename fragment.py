# code found in /spectral/io/envi.py as an example of save_image:

# Save the first 10 principal components of an image
data = open_image('92AV3C.lan').load()
pc = principal_components(data)
pcdata = pc.reduce(num=10).transform(data)
envi.save_image('pcimage.hdr', pcdata, dtype=np.float32)

