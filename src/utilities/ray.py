from dataclasses import dataclass

import numpy as np


@dataclass
class Ray:
    origin: np.array
    direction: np.array
