from abc import ABC
import numpy as np

class Sampler(ABC):
    def __init__(self, n=1):
        self._index = 0
        self._n = n
        self._data = np.array([])

    def all(self):
        return self._data

    def project_to_sphere(self, points):
        """
        Source: http://extremelearning.com.au/how-to-generate-uniformly-random-points-on-n-spheres-and-n-balls/
        Maps 2D ([0, 1] x [0, 1]) uniformly sampled points to 3D ([-1, 1]^3) uniformly sampled points on a 2-sphere. (Method 10)
        """
        u = points[:, 0]
        v = points[:, 1]

        theta = 2 * np.pi * u
        phi = np.arccos(2 * v - 1)

        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)

        self._data = np.vstack([x, y, z]).T
        assert self._data.shape == (self._n, 3)
        assert np.allclose(np.linalg.norm(self._data, axis=1), 1)

    def __next__(self):
        assert self._index < self._n, "no samples left"
        i = self._index
        self._index += 1
        return self._data[i, :]

class RandomSampler(Sampler):
    def __init__(self, n=1):
        Sampler.__init__(self, n)
        self.project_to_sphere(np.random.random(size=(n, 2)))
