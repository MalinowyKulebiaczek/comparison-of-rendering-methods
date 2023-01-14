import os
from multiprocessing import Pool

import numpy as np
from tqdm import tqdm

from procedure import MainProcedure
from renders.collision import get_collision
from utilities.bitmap import Bitmap
from utilities.ray import Ray

from renders.sampler import RandomSampler

PROCESS_PROCEDURE = None

"""
Comment by: Damian Łysomirski
I don't think this mapping is present, it is available for various samplers and we don't use them.
See:
https://en.wikipedia.org/wiki/Path_tracing
"""


def hemisphere_mapping(point: np.array, normal: np.array) -> np.array:
    if np.dot(point, normal) < 0:
        return -point
    else:
        return point


def random_three_vector():
    """
    Generates a random 3D unit vector (direction) with a uniform spherical distribution
    Algo from http://stackoverflow.com/questions/5408276/python-uniform-spherical-distribution
    :return:
    """
    u = np.random.random()
    v = np.random.random()

    theta = 2 * np.pi * u
    phi = np.arccos(2 * v - 1)

    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return np.array([x, y, z])


def path_trace(procedure: MainProcedure) -> Bitmap:
    """
    Main procedure:

    creates bitmap, renders each pixel from corresponding
    ray generated by camera.
    """
    procedure.load_scene()
    procedure.scene.load_camera()
    procedure.scene.load_lights()
    bitmap = Bitmap(*procedure.scene.camera.resolution)

    pool = Pool(os.cpu_count())
    tasks = []
    rays = procedure.scene.camera.generate_initial_rays()
    procedure.free_scene()
    np.random.shuffle(rays)
    batches = np.array_split(rays, os.cpu_count())

    with Pool(processes=os.cpu_count()) as pool:
        tasks = [
            pool.apply_async(trace_ray_task, (batch, procedure)) for batch in batches
        ]
        pool.close()
        pool.join()
        for task in tasks:
            for ((x, y), color) in task.get():
                bitmap[y, x] = color

    return bitmap


def trace_ray_task(batch, procedure_template: MainProcedure):
    """
    Task executed in Pool.
    """
    global PROCESS_PROCEDURE

    if PROCESS_PROCEDURE is None:
        PROCESS_PROCEDURE = procedure_template
        PROCESS_PROCEDURE.load_scene()
        PROCESS_PROCEDURE.load_background()
        PROCESS_PROCEDURE.scene.load_objects()
        PROCESS_PROCEDURE.scene.load_materials()
        PROCESS_PROCEDURE.scene.load_lights()

    colors = []
    samples = PROCESS_PROCEDURE.samples

    for (x, y), ray in tqdm(batch):
        result = np.array([0.0, 0.0, 0.0])
        for _ in range(samples):
            result += trace_ray(PROCESS_PROCEDURE, ray)
        result = (result / samples * 255).astype("uint8")
        colors.append(((x, y), result))

    return colors


def trace_ray(
    procedure: MainProcedure,
    ray: Ray,
    # sampler: RandomSampler, #Wydaje mi się
    depth: int = 0,
) -> np.array:
    """
    Trace ray
    """
    if depth > procedure.max_depth:
        return background(procedure, ray)

    hit = get_collision(ray, procedure.scene)

    if hit is None:
        return background(procedure, ray)

    new_ray = Ray(
        origin=hit.coords,
        direction=hemisphere_mapping(
            random_three_vector(), hit.normal
        ),  # Tu mi się wydaje ze moze blad być
    )

    probability = 1 / (2 * np.pi)

    hit_material = procedure.scene.get_material(hit.material_id)

    emmitance = hit_material.emmitance

    #if emmitance[0] > 0:
    #    return emmitance

    cos_theta = np.dot(new_ray.direction, hit.normal)

    """
    Na wikipedi jest inaczej z tym brdf ?
    """

    #brdf = (hit_material.diffusion * cos_theta) + (  # diffusion brdf
    #    hit_material.reflectance  # reflectance = specular w .dae
    #    * (np.dot(ray.direction, new_ray.direction) ** hit_material.shininess)
    #)  # reflectance brdf
    brdf = hit_material.reflectance / np.pi
    #brdf = hit_material.diffusion * np.max(cos_theta, 0)

    incoming = trace_ray(procedure, new_ray, depth + 1)

    direct_lighting = np.zeros(3) # initialize empty direct lighting value
    for light in procedure.scene.lights:
        # calculate the direct lighting contribution from each light source
        light_direction = light.position - hit.coords
        light_distance = np.linalg.norm(light_direction)
        light_direction = light_direction / light_distance
        
        shadow_ray = Ray(origin=hit.coords, direction=light_direction)
        hit_between_object_and_light = get_collision(shadow_ray, procedure.scene)
        if hit_between_object_and_light is None or \
                calculate_distance(hit.coords, hit_between_object_and_light.coords) >= calculate_distance(hit.coords, light.position):
            # if there is no collision, the point is not in shadow
            #direct_lighting += (light.intensity / (light_distance ** 2)) * np.maximum(np.dot(light_direction, hit.normal), 0) * hit_material.diffusion
            direct_lighting +=  hit_material.diffusion *  np.dot(light_direction, hit.normal)

    # RENDER EQUATION
    return (incoming * brdf * cos_theta / probability) + direct_lighting


def background(
    procedure: MainProcedure,
    ray: Ray,
) -> np.array:
    """
    Gets environment map value for the ray
    or returns black other way
    """
    return procedure.background(ray)

def calculate_distance(p1, p2):
    squared_dist = np.sum((p1-p2)**2, axis=0)
    return np.sqrt(squared_dist)
