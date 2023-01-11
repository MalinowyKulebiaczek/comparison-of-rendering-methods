from typing import Any, Optional

import numpy as np

from scenecomponents.scene import Scene
from utilities.ray import Ray

np.seterr(divide = 'ignore') 

class Hit:
    def __init__(
            self,
            triangle: Any,
            u: float,
            v: float,
            distance: float,
            hit_object: Any,
            ray: Ray,
    ):
        self.u = u
        self.v = v
        self.distance = distance
        self.hit_object = hit_object
        self.ray = ray
        self.triangle = triangle
        self._normal = None
        self._coords = None

    def _calculate_normal(self):
        """
        TODO right now that just
        copies triangle normal
        """
        def normalize(vector):
            return vector / np.linalg.norm(vector)

        dir = np.cross(self.triangle.vertices[1] - self.triangle.vertices[0],
                       self.triangle.vertices[2] - self.triangle.vertices[0])
        self._normal = normalize(dir)

    def _calculate_coords(self):
        self._coords = self.ray.origin + self.ray.direction * self.distance

    @property
    def normal(self):
        if self._normal is None:
            self._calculate_normal()

        return self._normal

    @property
    def coords(self):
        if self._coords is None:
            self._calculate_coords()

        return self._coords

    @property
    def material_id(self):
        return self.triangle.material.id


def get_collision(
        ray: Ray,
        scene: Scene,
) -> Optional[Hit]:
    """
    Calculates collision for given ray
    on procedures scene. Returns hit object.
    """
    hit = None

    for obj in scene.objects:
        if hits_bounding_box(ray, obj):
            # ray inside object
            for primitive in obj.primitives:
                if hits_bounding_box(ray, primitive):
                    # ray inside object's primitive
                    for triangle in primitive.triangles:
                        # checking every triangle
                        hit_ = intersect(ray, triangle, obj)
                        if hit_ and (hit is None or hit_.distance < hit.distance):
                            # most close hit
                            hit = hit_

    return hit


def hits_bounding_box(ray: Ray, obj: Any) -> bool:
    """
    Checks if ray hits bounding box of object
    """
    box = obj.bounding_box
    box_matrix = np.array([box.lower_bound, box.upper_bound])
    t = np.sort(np.matrix.transpose((box_matrix - ray.origin) / ray.direction))
    t_s = np.max(t[:, 0])
    t_e = np.min(t[:, 1])

    return all(t[:, 1] >= 0.0) and t_e >= t_s


def intersect(ray: Ray, triangle, object_) -> Optional[Hit]:
    """
    Calculates if ray will hit the triangle.

    Returns tuple:
        (
            did_ray_hit_something: bool,
            (
                time: float,
                u: np.array[float],
                v: np.array[float],
            ),
        )
    """

    # break down triangle into the individual points
    v1, v2, v3 = triangle.vertices
    eps = 0.000001

    # compute edges
    edge1 = v2 - v1
    edge2 = v3 - v1
    pvec = np.cross(ray.direction, edge2)
    det = edge1.dot(pvec)

    if abs(det) < eps:  # no intersection
        return None

    inv_det = 1.0 / det
    tvec = ray.origin - v1
    u = tvec.dot(pvec) * inv_det

    if u < 0.0 or u > 1.0:  # if not intersection
        return None

    qvec = np.cross(tvec, edge1)
    v = ray.direction.dot(qvec) * inv_det
    if v < 0.0 or u + v > 1.0:  # if not intersection
        return None

    t = edge2.dot(qvec) * inv_det
    if t < eps:
        return None

    return Hit(
        triangle=triangle,
        ray=ray,
        distance=t,
        u=u,
        v=v,
        hit_object=object_,
    )
