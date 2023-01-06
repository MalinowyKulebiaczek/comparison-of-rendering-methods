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


def reflected(vector, axis):
    return vector - 2 * np.dot(vector, axis) * axis


def sphere_intersect(center, radius, ray_origin, ray_direction):
    b = 2 * np.dot(ray_direction, ray_origin - center)
    c = np.linalg.norm(ray_origin - center) ** 2 - radius ** 2
    delta = b ** 2 - 4 * c
    if delta > 0:
        t1 = (-b + np.sqrt(delta)) / 2
        t2 = (-b - np.sqrt(delta)) / 2
        if t1 > 0 and t2 > 0:
            return min(t1, t2)
    return None


def nearest_intersected_object(objects, ray_origin, ray_direction):
    distances = [sphere_intersect(obj['center'], obj['radius'], ray_origin, ray_direction) for obj in objects]
    nearest_object = None
    min_distance = np.inf
    for index, distance in enumerate(distances):
        if distance and distance < min_distance:
            min_distance = distance
            nearest_object = objects[index]
    return nearest_object, min_distance


width = 300
height = 200

max_depth = 1

camera = np.array([0, 0, 1])
ratio = float(width) / height
screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom

light = {'position': np.array([5, 5, 5]), 'ambient': np.array([1, 1, 1]), 'diffuse': np.array([1, 1, 1]),
         'specular': np.array([1, 1, 1])}

objects = [
    {'center': np.array([-0.2, 0, -1]), 'radius': 0.7, 'ambient': np.array([0.1, 0, 0]),
     'diffuse': np.array([0.7, 0, 0]), 'specular': np.array([1, 1, 1]), 'shininess': 100, 'reflection': 0.5},
    {'center': np.array([0.1, -0.3, 0]), 'radius': 0.1, 'ambient': np.array([0.1, 0, 0.1]),
     'diffuse': np.array([0.7, 0, 0.7]), 'specular': np.array([1, 1, 1]), 'shininess': 100, 'reflection': 0.5},
    {'center': np.array([-0.3, 0, 0]), 'radius': 0.15, 'ambient': np.array([0, 0.1, 0]),
     'diffuse': np.array([0, 0.6, 0]), 'specular': np.array([1, 1, 1]), 'shininess': 100, 'reflection': 0.5},
    # { 'center': np.array([0, -9000, 0]), 'radius': 9000 - 0.7, 'ambient': np.array([0.1, 0.1, 0.1]), 'diffuse': np.array([0.6, 0.6, 0.6]), 'specular': np.array([1, 1, 1]), 'shininess': 100, 'reflection': 0.5 }
]


# image = np.zeros((height, width, 3))
# for i, y in enumerate(tqdm(np.linspace(screen[1], screen[3], height))):
#     for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
#         # screen is on origin
#         pixel = np.array([x, y, 0])
#         origin = camera
#         direction = normalize(pixel - origin)
#
#         color = np.zeros((3))
#         reflection = 1
#
#         for k in range(max_depth):
#             # check for intersections
#             nearest_object, min_distance = nearest_intersected_object(objects, origin, direction)
#             if nearest_object is None:
#                 break
#
#             intersection = origin + min_distance * direction
#             normal_to_surface = normalize(intersection - nearest_object['center'])
#             shifted_point = intersection + 1e-5 * normal_to_surface
#             intersection_to_light = normalize(light['position'] - shifted_point)
#
#             _, min_distance = nearest_intersected_object(objects, shifted_point, intersection_to_light)
#             intersection_to_light_distance = np.linalg.norm(light['position'] - intersection)
#             is_shadowed = min_distance < intersection_to_light_distance
#
#             if is_shadowed:
#                 break
#
#             illumination = np.zeros((3))
#
#             # ambiant
#             illumination += nearest_object['ambient'] * light['ambient']
#
#             # diffuse
#             illumination += nearest_object['diffuse'] * light['diffuse'] * np.dot(intersection_to_light,
#                                                                                   normal_to_surface)
#
#             # specular
#             intersection_to_camera = normalize(camera - intersection)
#             H = normalize(intersection_to_light + intersection_to_camera)
#             illumination += nearest_object['specular'] * light['specular'] * np.dot(normal_to_surface, H) ** (
#                     nearest_object['shininess'] / 4)
#             #
#             # # reflection
#             # color += reflection * illumination
#             # reflection *= nearest_object['reflection']
#             #
#             # origin = shifted_point
#             # direction = reflected(direction, normal_to_surface)
#
#             image[i, j] = np.clip(illumination, 0, 1)
#     # print("%d/%d" % (i + 1, height))
#
# plt.imsave('image.png', image)

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

    batches = np.array_split(rays, 60)

    for batch in tqdm(batches):
        pool = Pool(os.cpu_count())
        tasks = {}
        for (x, y), ray in batch:
            tasks[(x, y)] = pool.apply_async(trace_ray_task, (ray, procedure))
        pool.close()
        pool.join()
        for i, (x, y) in enumerate(tasks.keys()):
            bitmap[y, x] = tasks[(x, y)].get()
            
    return bitmap

def trace_ray_task(ray: Ray, procedure_template: MainProcedure):    
    global PROCESS_PROCEDURE

    if PROCESS_PROCEDURE is None:
        PROCESS_PROCEDURE = procedure_template
        PROCESS_PROCEDURE.load_scene()
        PROCESS_PROCEDURE.load_background()
        PROCESS_PROCEDURE.scene.load_objects()
        PROCESS_PROCEDURE.scene.load_materials()
        PROCESS_PROCEDURE.scene.load_lights()
        PROCESS_PROCEDURE.scene.load_camera()

    color = trace_ray(PROCESS_PROCEDURE, ray)
    return np.clip(color, 0, 1)

def trace_ray(procedure, ray):
    camera = procedure.scene.camera
    origin = camera.origin
    color = np.zeros(3)
    hit = get_collision(ray, procedure.scene)
    if hit is None:
        color = background(procedure, ray)
    else:
        light_shining_on_hit, direction_from_hitpoint_to_light = get_light_that_shines_on_point(procedure.scene,
                                                                                                hit.coords)
        if light_shining_on_hit is not None:
            hit_material = procedure.scene.get_material(hit.material_id)
            direction_from_point_to_camera = normalize(origin - hit.coords)
            color = get_blinn_phong(hit_material, light_shining_on_hit, direction_from_hitpoint_to_light,
                                    direction_from_point_to_camera, hit.normal)
    return color


def get_light_that_shines_on_point(scene: Scene, point):
    for light in scene.lights:
        direction_from_point_to_light = normalize(light.position - point)
        ray = Ray(origin=point, direction=direction_from_point_to_light)
        hit = get_collision(ray, scene)
        if hit is None:
            # if there is no object between the point and light then it means this light shines on object
            return light, direction_from_point_to_light
    return None, None


def get_blinn_phong(hit_material, light, direction_from_point_to_light, direction_from_point_to_camera,
                    normal_to_surface):
    illumination = np.zeros(3)
    # ambient
    illumination += hit_material.ambient * light.color  # tbh should probably be sth like light.ambient but lgith seems noty to have such field
    # diffuse
    illumination += hit_material.diffusion * np.dot(direction_from_point_to_light, normal_to_surface)
    # specular
    H = normalize(direction_from_point_to_light + direction_from_point_to_camera)
    illumination += hit_material.specular * np.dot(normal_to_surface, H) ** (hit_material.shininess / 4)

    # TODO dorobic reflection
    # color = np.zeros(3)
    # reflection = 1
    # color += reflection * illumination
    # reflection *= hit_material.emmitance

    return illumination


if __name__ == '__main__':
    file_dae = "scenes/spheres_color.dae"
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
        environment_map=environment_map
    )  # .render(output_file)

    procedure.load_scene()
    procedure.load_background()
    procedure.scene.load_objects()
    procedure.scene.load_materials()
    procedure.scene.load_lights()
    procedure.scene.load_camera()

    MAX_DEPTH = 1
    ray_tracing_render(procedure, MAX_DEPTH)
