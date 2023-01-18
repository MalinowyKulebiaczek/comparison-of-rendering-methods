import os
from multiprocessing import Pool, Value
import time
import numpy as np
from tqdm import tqdm

from procedure import MainProcedure
from renders.collision import get_collision, calc_triangles
from renders.pathtracing.pathtrace import background
from scenecomponents.scene import Scene
from utilities.bitmap import Bitmap
from utilities.ray import Ray

process_procedure = None
intersections = None
shadow_rays = None


def normalize(vector):
    return vector / np.linalg.norm(vector)

def init_worker(procedure: MainProcedure, intersection_count, shadow_rays_count):
    global process_procedure
    global intersections
    global shadow_rays

    if process_procedure is None:
        process_procedure = procedure
        process_procedure.load_scene()
        process_procedure.load_background()
        process_procedure.scene.load_objects()
        process_procedure.scene.load_materials()
        process_procedure.scene.load_lights()
        process_procedure.scene.load_camera()
    if intersections is None:
        intersections = intersection_count
    if shadow_rays is None:
        shadow_rays = shadow_rays_count

def increment_intersection_counter():
    with intersections.get_lock():
        intersections.value += 1

def increment_shadow_rays_counter():
    with shadow_rays.get_lock():
        shadow_rays.value += 1

def ray_tracing_render(procedure: MainProcedure, max_depth):
    time_start = time.time()
    intersection_count = Value("i", 0)
    shadow_rays_count = Value("i", 0)
    init_worker(procedure=procedure, intersection_count=intersection_count, shadow_rays_count=shadow_rays_count)
    number_of_traingles = calc_triangles(procedure.scene)
    rays = procedure.scene.camera.generate_initial_rays()
    np.random.shuffle(rays)
    bitmap = Bitmap(*procedure.scene.camera.resolution)

    procedure.free_scene()

    with Pool(
        processes=os.cpu_count(),
        initializer=init_worker,
        initargs=(procedure, intersection_count, shadow_rays_count),
    ) as pool:
        with tqdm(total=len(rays), mininterval=2) as pbar:
            for ((x, y), color) in pool.imap_unordered(trace_ray_task, rays):
                bitmap[y, x] = color
                pbar.update()

    elapsed_time = time.time() - time_start


    process_procedure.set_statistic("Number of triangles", number_of_traingles)
    process_procedure.set_statistic("Intersections", intersections.value)
    process_procedure.set_statistic("Number of shadow rays", shadow_rays.value)
    process_procedure.set_statistic("Total time", str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
    return bitmap


def trace_ray_task(initial_ray):
    # initial_ray is (coords of ray, ray)
    color = trace_ray(initial_ray[1])
    return (initial_ray[0], np.clip(color, 0, 255))


def trace_ray(ray):
    hit = get_collision(ray, process_procedure.scene)
    if hit is None:
        color = background(process_procedure, ray)
    else:
        color = color_at(hit, process_procedure.scene)
        increment_intersection_counter()
    return (color * 255).astype("uint8")


def get_light_that_shines_on_point(scene: Scene, point):
    for light in scene.lights:
        direction_from_point_to_light = normalize(light.position - point)
        ray = Ray(origin=point, direction=direction_from_point_to_light)
        hit = get_collision(ray, scene)
        if hit is None:
            # if there is no object between the point and light then it means this light shines on object
            return light, direction_from_point_to_light
    return None, None


def color_at(hit, scene):
    hit_material = scene.get_material(hit.material_id)
    color = np.zeros(3)

    for light in scene.lights:

        direction_from_hit_to_light = normalize(light.position - hit.coords)
        ray = Ray(origin=hit.coords, direction=direction_from_hit_to_light)
        hit_between_object_and_light = get_collision(ray, scene)
        if hit_between_object_and_light is None or \
                calculate_distance(hit.coords, hit_between_object_and_light.coords) >= calculate_distance(hit.coords, light.position):
            # if there is no object between the point and light then it means this light shines on object

            # diffuse
            color += (
                hit_material.diffusion
                * np.dot(direction_from_hit_to_light, hit.normal)
                * light_attenuation(light, hit)
            )

        # calculate shadow rays
        else:
            increment_shadow_rays_counter()

    return color


def light_attenuation(light, hit):
    # constant after / is for scaling the light's brightness
    return np.average(light.color) / (
        500 * np.linalg.norm(light.position - hit.coords) ** 2 + 1000
    )


def calculate_distance(p1, p2):
    squared_dist = np.sum((p1 - p2) ** 2, axis=0)
    return np.sqrt(squared_dist)
