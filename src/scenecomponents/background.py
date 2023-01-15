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
        # Calculate the unit vector in the direction of the ray
        direction = ray.direction / np.linalg.norm(ray.direction)
        offset_x = 0
        offset_y = 0
        cube_width = self.environment_map.shape[1] / 4

        # Determine which face of the cube the ray is pointing towards
        if abs(direction[0]) >= abs(direction[1]) and abs(direction[0]) >= abs(
            direction[2]
        ):
            # Ray is pointing towards the left or right face of the cube
            offset_y = cube_width
            u = direction[2] / abs(direction[0])
            v = -direction[1] / abs(direction[0])
            if direction[0] >= 0:
                # Ray is pointing towards the right face of the cube
                offset_x = 0
            else:
                # Ray is pointing towards the left face of the cube
                offset_x = cube_width * 2
                u *= -1
        elif abs(direction[1]) >= abs(direction[0]) and abs(direction[1]) >= abs(
            direction[2]
        ):
            # Ray is pointing towards the top or bottom face of the cube
            offset_x = cube_width
            u = -direction[0] / abs(direction[1])
            v = direction[2] / abs(direction[1])
            if direction[1] >= 0:
                # Ray is pointing towards the top face of the cube
                offset_y = 0
            else:
                # Ray is pointing towards the bottom face of the cube
                offset_y = 2 * cube_width
        else:
            # Ray is pointing towards the front or back face of the cube
            offset_y = cube_width
            u = direction[0] / abs(direction[2])
            v = -direction[1] / abs(direction[2])
            if direction[2] >= 0:
                # Ray is pointing towards the front face of the cube
                offset_x = cube_width
                u *= -1
            else:
                # Ray is pointing towards the back face of the cube
                offset_x = cube_width * 3

        # Convert the u and v coordinates to image coordinates
        map_x = (u + 1) / 2 * cube_width + offset_x
        map_y = (v + 1) / 2 * cube_width + offset_y

        # Make sure the image coordinates are within the bounds of the face image
        map_x = np.clip(map_x, 0, self.environment_map.shape[1] - 1)
        map_y = np.clip(map_y, 0, self.environment_map.shape[0] - 1)
        # Return the pixel at the calculated image coordinates
        return self.environment_map[int(map_y), int(map_x)]

    def __call__(self, ray: Ray):
        return self.color(ray)
