import numpy as np


class Photon:
    def __init__(
        self, position: np.array, normal: np.array, color: np.array, direction: np.array
    ):
        self.position = position
        self.normal = normal
        self.color = color
        self.direction = direction
