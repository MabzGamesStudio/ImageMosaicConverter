import random
from PIL import Image
import numpy as np
from scipy.spatial import KDTree

class Nodes:
    def __init__(self, image_pixels, width, height, num_nodes, batches=5):
        self.points_set = set() # Set of pixel position and pixel color tuples
        self.points = [] # List of mosaic points
        self.colors = [] # List of mosaic colors
        self.width = width # Image width
        self.height = height # Image height
        self.image_pixels = image_pixels # Pixel data of image
        self.num_nodes = num_nodes # Number of mosaic nodes
        self.batches = batches # Number of batches to process 
        self.formatted_pixels = None # Pixel data of mosaic image

        # Pixel data of difference between actual image pixel and mosaic pixel
        self.difference_pixels = np.full((width * height, 3), (255, 255, 255), dtype=np.uint8)

        # Place nodes in batches to concentrate nodes in high detail areas
        for i in range(self.batches):
            self.next_batch(int((((i+1) / batches) ** 2) * self.num_nodes))
            self.get_formatted_pixels()
            self.get_difference_pixels()

    def next_batch(self, num_points):

        # Add points until num_points reached
        while len(self.points_set) < num_points:
            random_position = random.randint(0, self.width * self.height - 1)

            # Place nodes more in high detail areas
            if random.randint(0, 255) ** 2 >= self.difference_pixels[random_position, 0]:
                continue
            
            # Add the point to the node set
            self.points_set.add((
                    random_position // self.width,
                    random_position % self.width,
                    tuple(self.image_pixels[random_position])
            ))

        # Convert node set to separate pixel list and color list
        points_set_list = list(self.points_set)
        self.points = np.array([[p[0], p[1]] for p in points_set_list])
        self.colors = np.array([c[2] for c in points_set_list], dtype=np.uint8)

        # kd-tree to find closest node for all pixels
        self.tree = KDTree(self.points)

    # Gets the mosaic pixels by finding the closest node and copying that pixel color value
    def get_formatted_pixels(self):
        indices = np.arange(self.width * self.height)
        coords = np.column_stack((indices // self.width, indices % self.width))
        _, nearest_indices = self.tree.query(coords)
        self.formatted_pixels = self.colors[nearest_indices]
        return self.formatted_pixels
        
    # Gets the difference in color between actual image pixels and mosaic pixels
    def get_difference_pixels(self):        
        pixels_difference = np.abs(self.get_formatted_pixels() - self.image_pixels)
        pixels_gray = np.dot(pixels_difference, [.333, .333, .333])
        self.difference_pixels = np.concatenate(([pixels_gray], [pixels_gray], [pixels_gray]), axis=0).T
        return self.difference_pixels
    
    # Saves the mosaic image as a png
    def save_image(self, pixels, width, height, name):
        pixels = np.array(pixels, dtype=np.uint8)
        pixels_reshaped = pixels.reshape((height, width, 3))
        image = Image.fromarray(pixels_reshaped)
        image.save(f'{name}.png')
        print(f'Saved {name}.png!')
