from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == "__main__":
    file_dae = "src/scenes/path_tracing_scene.dae"
    resolution = 200
    samples = 4
    max_depth = 2
    environment_map = "src/scenes/skbx.jpg"
    n_photons = 50000

    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth,
        environment_map=environment_map,
    ).renderPhotonMap(output_file, n_photons)
    #    ).renderRayTrace(output_file)
     #).renderPathTrace(output_file)
