import numpy as np

ZEROES = np.array([0.0, 0.0, 0.0])


class Material:
    def __init__(self, material):
        self._material = material

    @property
    def emmitance(self):
        """
        idk if we can just do it like that
        """
        return np.array((self._material.effect.emission or ZEROES)[:3])

    @property
    def reflectance(self):
        return self._material.effect.reflectivity or 0.0

    @property
    def diffusion(self):
        return np.array((self._material.effect.diffuse or ZEROES)[:3])

    @property
    def index_of_refraction(self):
        return self._material.effect.index_of_refraction

    @property
    def shiness(self):
        return self._material.effect.shininess or 0.0
