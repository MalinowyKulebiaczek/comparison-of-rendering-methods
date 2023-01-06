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
    origin = ray.origin
    color = np.zeros(3)
    hit = get_collision(ray, procedure.scene)
    if hit is None:
        color = background(procedure, ray)
    else:
        (
            light_shining_on_hit,
            direction_from_hitpoint_to_light,
        ) = get_light_that_shines_on_point(procedure.scene, hit.coords)
        if light_shining_on_hit is not None:
            hit_material = procedure.scene.get_material(hit.material_id)
            direction_from_point_to_camera = normalize(origin - hit.coords)
            color = calculate_shading(
                hit_material,
                light_shining_on_hit,
                direction_from_hitpoint_to_light,
                direction_from_point_to_camera,
                hit.normal,
            )
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


def calculate_shading(
    hit_material,
    light,
    direction_from_point_to_light,
    direction_from_point_to_camera,
    normal_to_surface,
):
    illumination = np.zeros(3)
    # ambient
    illumination += (
        hit_material.ambient * light.color
    )  # tbh should probably be sth like light.ambient but lgith seems noty to have such field
    # diffuse
    illumination += hit_material.diffusion * np.dot(
        direction_from_point_to_light, normal_to_surface
    )
    # specular
    H = normalize(direction_from_point_to_light + direction_from_point_to_camera)
    illumination += hit_material.specular * np.dot(normal_to_surface, H) ** (
        hit_material.shininess / 4
    )

    # TODO dorobic reflection
    # color = np.zeros(3)
    # reflection = 1
    # color += reflection * illumination
    # reflection *= hit_material.emmitance

    return illumination


if __name__ == "__main__":
    file_dae = "scenes/spheres_color_working.dae"
    resolution = 200
    samples = 8
    max_depth = 3
    environment_map = "scenes/env.jpg"

    scene = Scene.load(file_dae, 200)
    output_file = "out.png"

    procedure = MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth,
        environment_map=environment_map,
    )  # .render(output_file)

    procedure.load_scene()
    procedure.load_background()
    procedure.scene.load_objects()
    procedure.scene.load_materials()
    procedure.scene.load_lights()
    procedure.scene.load_camera()

    MAX_DEPTH = 1
    ray_tracing_render(procedure, MAX_DEPTH)
