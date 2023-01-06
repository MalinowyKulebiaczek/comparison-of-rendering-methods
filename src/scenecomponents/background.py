import numpy as np
from PIL import Image

from utilities.bitmap import color
from utilities.ray import Ray


class Background:
    def __init__(self, background_color, environment_map):
        self.color = None
        self.environment_map = None

        if background_color is not None:
            self.color = lambda x: background_color
        elif environment_map is not None:
            with Image.open(environment_map) as im:
                self.environment_map = np.array(im) / 255
            self.color = self.color_from_map
        else:
            self.color = lambda x: color(0, 0, 0)

    def color_from_map(self, ray: Ray):
        # Calculate the spherical coordinates of the ray direction
        theta = np.arctan2(ray.direction[1], ray.direction[0])
        phi = np.arccos(ray.direction[2])

        # Convert the spherical coordinates to image coordinates
        map_x = (theta + np.pi) / (2 * np.pi) * self.environment_map.shape[1]
        map_y = (phi + np.pi / 2) / np.pi * self.environment_map.shape[0]

        # Make sure the image coordinates are within the bounds of the hdri map
        map_x = np.clip(map_x, 0, self.environment_map.shape[1] - 1)
        map_y = np.clip(map_y, 0, self.environment_map.shape[0] - 1)
        # Return the pixel at the calculated image coordinates
        return self.environment_map[int(map_y), int(map_x)]

    def __call__(self, ray: Ray):
        return self.color(ray)
