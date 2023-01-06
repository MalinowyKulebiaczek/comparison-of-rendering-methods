import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import os
from multiprocessing import Pool
from utilities.bitmap import Bitmap

from procedure import MainProcedure
from scenecomponents.scene import Scene
from renders.collision import get_collision
from renders.pathtracing.pathtrace import background
from utilities.ray import Ray

PROCESS_PROCEDURE = None


# na razie zostawiam ten kod z tutoriala tak brzydko zakomentowany - posprzatam potem
def normalize(vector):
    return vector / np.linalg.norm(vector)


def ray_tracing_render(procedure: MainProcedure, max_depth):
    procedure.load_scene()
    procedure.load_background()

    # procedure.scene.load_objects()
    # procedure.scene.load_materials()
    # procedure.scene.load_lights()
    procedure.scene.load_camera()

    rays = procedure.scene.camera.generate_initial_rays()

    bitmap = Bitmap(*procedure.scene.camera.resolution)
    print(procedure.scene.camera.resolution)

    procedure.free_scene()
    np.random.shuffle(rays)
    batches = np.array_split(rays, os.cpu_count())
    tasks = []
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
    global PROCESS_PROCEDURE

    if PROCESS_PROCEDURE is None:
        PROCESS_PROCEDURE = procedure_template
        PROCESS_PROCEDURE.load_scene()
        PROCESS_PROCEDURE.load_background()
        PROCESS_PROCEDURE.scene.load_objects()
        PROCESS_PROCEDURE.scene.load_materials()
        PROCESS_PROCEDURE.scene.load_lights()

    colors = []

    for (x, y), ray in tqdm(batch):
        color = trace_ray(PROCESS_PROCEDURE, ray)
        colors.append(((x, y), np.clip(color, 0, 255)))
    return colors


def trace_ray(procedure, ray):
    hit = get_collision(ray, procedure.scene)
    if hit is None:
        color = background(procedure, ray)
    else:
        color = color_at(hit, procedure.scene)
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
    ambient = [0.1, 0.1, 0.1]  # hit_material.ambient jest zawsze 0, wiec zahardkodowalem 0.1
    light_color = (1, 1, 1) # TODO normalizowac light.color po ludzku a nie uzywac zahardkodowanej wartosci
    # direction_from_hit_to_camera = normalize(scene.camera.origin - hit.coords)
    for light in scene.lights:
        direction_from_point_to_light = normalize(light.position - hit.coords)
        ray = Ray(origin=hit.coords, direction=direction_from_point_to_light)
        hit_between_object_and_light = get_collision(ray, scene)
        if hit_between_object_and_light is None:
            # if there is no object between the point and light then it means this light shines on object
            color += np.multiply(ambient, light_color)

            # diffuse
            direction_from_hit_to_light = normalize(light.position - hit.coords)
            color += hit_material.diffusion * np.dot(direction_from_hit_to_light, hit.normal)

            # specular - cytujac klasyka 'something is no yes' w tym miejscu, wiec wywalilem
            # H = normalize(direction_from_hit_to_light + direction_from_hit_to_camera)
            # color += light.color * hit_material.reflectance * max(np.dot(hit.normal, H), 0) ** (hit_material.shininess / 4)

    return color


