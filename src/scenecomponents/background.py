import numpy as np
from PIL import Image

from src.utilities.bitmap import color
from src.utilities.ray import Ray


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
        map_x = (
            (np.arctan(ray.direction[1] / ray.direction[0]) / np.pi + 1)
            / 2
            * self.environment_map.shape[1]
        )
        map_y = (
            (np.arctan(ray.direction[2] / ray.direction[0]) / np.pi + 1)
            / 2
            * self.environment_map.shape[0]
        )
        return self.environment_map[int(map_y), int(map_x)]

    def __call__(self, ray: Ray):
        return self.color(ray)
