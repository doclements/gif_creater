from images2gif import writeGif
from PIL import Image
import os


file_names = sorted((fn for fn in os.listdir('.') if fn.endswith('.png')))
images = [Image.open(fn) for fn in file_names]
filename = "my_gif55.gif"
writeGif(filename, images, duration=0.2, dispose=2)
