from dataclasses import dataclass

import numpy as np


@dataclass
class BoundingBox:
    lower_bound: np.array
    upper_bound: np.array


class Primitive:
    def __init__(self, primitive):
        self._primitive = primitive
        self._triangles = None
        self._bounding_box = None

    @property
    def triangles(self):
        if self._triangles is None:
            self._triangles = [x for x in self._primitive]
        return self._triangles

    @property
    def bounding_box(self):
        if self._bounding_box is None:
            self.generate_bounding_box()

        return self._bounding_box

    def generate_bounding_box(self):
        vertices = np.array([v for v in self._primitive.vertex])

        self._bounding_box = BoundingBox(
            lower_bound=vertices.min(axis=0),
            upper_bound=vertices.max(axis=0),
        )


class Object:
    """
    Geometry object with assigned material
    """

    def __init__(self, geometry):
        self._geometry = geometry
        self._primitives = None
        self._bounding_box = None

    @property
    def primitives(self):
        if self._primitives is None:
            self._primitives = [Primitive(x) for x in self._geometry.primitives()]

        return self._primitives

    @property
    def bounding_box(self):
        if self._bounding_box is None:
            self.generate_bounding_box()

        return self._bounding_box

    def generate_bounding_box(self):
        upper = np.array([p.bounding_box.upper_bound for p in self.primitives])
        lower = np.array([p.bounding_box.lower_bound for p in self.primitives])

        self._bounding_box = BoundingBox(
            lower_bound=lower.min(axis=0),
            upper_bound=upper.max(axis=0),
        )
