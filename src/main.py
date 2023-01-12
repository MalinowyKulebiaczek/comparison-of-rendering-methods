from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == "__main__":
    file_dae = "src/scenes/sphere_and_cubes_closer_light.dae"
    resolution = 200
    samples = 8
    max_depth = 3
    environment_map = "src/scenes/skbx.jpg"
    n_photons = 1000

    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth,
        environment_map=environment_map,
    ).renderPhotonMap(output_file, n_photons)
        #).renderRayTrace(output_file)
    # ).renderPathTrace(output_file)
