from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == "__main__":
    file_dae = "scenes/sphere_and_cubes_colour.dae"
    resolution = 200
    samples = 8
    max_depth = 3
    environment_map = "scenes/skbx.jpg"

    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth,
        environment_map=environment_map,
        ).renderRayTrace(output_file)
    # ).renderPathTrace(output_file)
