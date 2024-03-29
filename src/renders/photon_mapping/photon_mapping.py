import math
import numpy as np
from scipy.spatial import KDTree
import os
from multiprocessing import Pool, Value
from tqdm import tqdm
import time
from procedure import MainProcedure
from renders.collision import get_collision, calc_triangles
from renders.pathtracing.pathtrace import background
from scenecomponents.scene import Scene
from utilities.bitmap import Bitmap
from utilities.ray import Ray
from renders.photon_mapping.photon import Photon

process_procedure = None
intersections = None
shadow_rays = None

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

def generate_random_direction():
    # Generate random values for the spherical coordinates
    theta = 2 * math.pi * np.random.random()
    phi = math.acos(2 * np.random.random() - 1)

    # Convert the spherical coordinates to cartesian coordinates
    coords = np.zeros(3)
    coords[0] = math.sin(phi) * math.cos(theta)
    coords[1] = math.sin(phi) * math.sin(theta)
    coords[2] = math.cos(phi)

    # Return the generated direction vector
    return coords

def hemisphere_mapping(point: np.array, normal: np.array) -> np.array:
    if np.dot(point, normal) < 0:
        return -point
    else:
        return point

def generate_photon_map(light_source, scene, num_photons, max_depth):
    # Initialize the photon map
    photon_map = []
    print("GENERATING PHOTON MAP")
    i = 1
    # Generate photons from the light source
    for i in tqdm(range(num_photons)):
        shoot_photon(photon_map, scene, light_source, max_depth)

    print("Shot", num_photons, "rays, got", len(photon_map), "photon hits")
    if num_photons > len(photon_map):
        print("Generating additional photons to get the required number")

    i = 1
    while len(photon_map) < num_photons:
        if i % 10000 == 0:
            print(
                "Shot", i, "extra photons, got", len(photon_map), "photon hits so far"
            )
        shoot_photon(photon_map, scene, light_source, max_depth)
        i += 1
    print("Done!")

    # Return the generated photon map
    return photon_map


def shoot_photon(photon_map, scene, light_source, max_depth):
    # Generate a random direction for the photon
    direction = generate_random_direction()
    # Create a ray for the photon
    ray = Ray(light_source.position, direction)

    # Trace the photon through the scene
    hit = get_collision(ray, scene)

    # If the photon hit an object
    if hit:
        increment_intersection_counter()
        hit_material = scene.get_material(hit.material_id)
        # Store the photon's information in the photon map
        color = hit_material.diffusion * light_attenuation(np.linalg.norm(hit.coords - light_source.position))
        photon_map.append(
            Photon(hit.coords, hit.normal, color, -1 * ray.direction)
        )

        # Generate new photons with Russian roulette
        # Assuming here reflectance is the albedo of the material
        j = 0
        while np.random.random() < hit_material.reflectance and j < max_depth:
            j += 1
            new_direction = hemisphere_mapping(generate_random_direction(), hit.normal)
            new_ray = Ray(hit.coords, new_direction)
            hit = get_collision(new_ray, scene)
            if hit:
                increment_intersection_counter()
                hit_material = scene.get_material(hit.material_id)
                color *= hit_material.diffusion 
                color *= light_attenuation(np.linalg.norm(hit.coords - light_source.position)) * 0.7
                photon_map.append(
                    Photon(
                        hit.coords,
                        hit.normal,
                        color,
                        -1 * ray.direction,
                    )
                )
            else:
                return


def search_photons(position, photon_map, photon_tree, num_photons=10):
    # Find the k nearest photons to the hit point
    _, indices = photon_tree.query(position, k=num_photons)
    if num_photons == 1:
        return [photon_map[indices]]
    return [photon_map[i] for i in indices]


def render_photon_mapping(procedure: MainProcedure, n_photons, max_depth) -> Bitmap:
    """
    Main procedure:

    creates bitmap, renders each pixel from corresponding
    ray generated by camera.
    """
    time_start = time.time()
    intersection_count = Value("i", 0)
    shadow_rays_count = Value("i", 0)
    init_worker(procedure=procedure, intersection_count=intersection_count, shadow_rays_count=shadow_rays_count)
    number_of_traingles = calc_triangles(procedure.scene)
    bitmap = Bitmap(*procedure.scene.camera.resolution)

    pool = Pool(os.cpu_count())
    tasks = []
    rays = procedure.scene.camera.generate_initial_rays()
    # assuming 1 light for now
    photon_map = []
    photon_tree = None
    for light in procedure.scene.lights:
        photon_map.extend(
            generate_photon_map(light, procedure.scene, n_photons, max_depth)
        )
        positions = np.array([p.position for p in photon_map])
        photon_tree = KDTree(positions)
    procedure.free_scene()
    np.random.shuffle(rays)
    batches = np.array_split(rays, os.cpu_count())

    with Pool(processes=os.cpu_count(), initializer=init_worker, initargs=(procedure,intersection_count, shadow_rays_count)) as pool:
        tasks = [
            pool.apply_async(
                trace_ray_task, (batch, photon_map, photon_tree)
            )
            for batch in batches
        ]
        pool.close()
        pool.join()
        for task in tasks:
            for ((x, y), color) in task.get():
                bitmap[y, x] = color
    
    elapsed_time = time.time() - time_start
    process_procedure.set_statistic("Number of triangles", number_of_traingles)
    process_procedure.set_statistic("Intersections", intersections.value)
    process_procedure.set_statistic("Number of shadow rays", shadow_rays.value)
    process_procedure.set_statistic("Total time", str(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))

    return bitmap


def trace_ray_task(batch, photon_map, photon_tree):
    """
    Task executed in Pool.
    """

    colors = []

    for (x, y), ray in tqdm(batch):
        result = trace_ray(ray, photon_map, photon_tree)
        result = (result * 255).astype("uint8")
        colors.append(((x, y), result))

    return colors


def trace_ray(ray: Ray, photon_map: np.array, photon_tree
) -> np.array:

    hit = get_collision(ray, process_procedure.scene)
    increment_intersection_counter()

    if hit is None:
        return background(process_procedure, ray)
    color = np.zeros(3)
    n=0
    # Search for the closest photons in the photon map to the hit point
    closest_photons = search_photons(hit.coords, photon_map, photon_tree, 50)
    #dist = np.linalg.norm(closest_photons[0].position - hit.coords)
    #return np.array([dist, dist, dist])
    hit_material = process_procedure.scene.get_material(hit.material_id)
    for photon in closest_photons:
        # Calculate the diffuse and specular reflection using the hit point's normal and the photon's direction
        diffuse_reflection = max(np.dot(hit.normal, photon.direction), 0)
        # specular_reflection = max(np.dot(hit.normal, (2 * photon.direction - ray.direction)), 0) ** hit.material.shininess
        # Calculate the final color by adding the contribution of the current photon to the color
        if np.linalg.norm(photon.position - hit.coords) <= 0.2:
            color += diffuse_reflection * photon.color * hit_material.diffusion #+ specular_reflection * photon.color * hit.material.specular
            n += 1
    return color / n# len(closest_photons)

def light_attenuation(dist):
    return 1 / (
        dist ** 2 + 1
    )
