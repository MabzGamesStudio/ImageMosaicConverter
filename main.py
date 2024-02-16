from PIL import Image
import numpy as np
from nodes import Nodes

# Processing input
image_path = 'Meme.jpg'
save_name = 'MemeMosaic'
mosaic_nodes = 1000

# Gets pixel array from image
image = Image.open(image_path)
width = image.width
height = image.height
pixels = np.array(image.getdata())

nodes = Nodes(pixels, width, height, mosaic_nodes)

# Saves the image
nodes.save_image(nodes.get_formatted_pixels(), width, height, save_name)
