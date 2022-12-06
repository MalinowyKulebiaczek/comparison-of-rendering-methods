from typing import List, Tuple

import numpy as np

from src.utilities.ray import Ray


class Camera:
    """
    Camera object, that generates initial
    rays and stores the result.
    """

    def __init__(self, camera, resolution):
        self._camera = camera
        self.image_height = resolution
        self.image_width = int(resolution * self.aspect_ratio)

    @property
    def resolution(self):
        return (self.image_width, self.image_height)

    @property
    def matrix(self):
        return self._camera.matrix

    @property
    def fov(self):
        return self._camera.xfov or self._camera.yfov

    @property
    def aspect_ratio(self):
        return self._camera.aspect_ratio

    def generate_initial_rays(self) -> List[Tuple[Tuple[int, int], Ray]]:
        """
        Generate initial rays, return list of tuples:
            (coords of ray, ray)
        """
        rays = []

        def normalize(v):
            norm = np.linalg.norm(v, ord=1)
            if norm == 0:
                norm = np.finfo(v.dtype).eps
            return v / norm

        origin = np.matmul(self.matrix, np.array([0, 0, 0, 1]))
        origin = origin[:3] / origin[3]

        for x in np.arange(self.image_width):
            px = (
                    (2 * ((x + 0.5) / self.image_width) - 1)
                    * np.tan(self.fov / 2 * np.pi / 180)
                    * self.aspect_ratio
            )
            for y in np.arange(self.image_height):
                py = (1 - 2 * ((y + 0.5) / self.image_height)) * np.tan(
                    self.fov / 2 * np.pi / 180
                )
                direction = np.matmul(self.matrix, np.array([px, py, -1, 1]))
                direction = direction[:3] / direction[3]
                direction = normalize(direction - origin)

                rays.append(
                    (
                        (x, y),
                        Ray(
                            origin=origin,
                            direction=direction,
                        ),
                    ),
                )

        return rays
