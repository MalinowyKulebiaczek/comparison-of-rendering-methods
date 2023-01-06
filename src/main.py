from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == '__main__':
    file_dae = "src/scenes/spheres.dae"
    resolution = 200
    samples = 8
    max_depth = 3
    environment_map="src/scenes/hdr_bg.jpg"

    scene = Scene.load(file_dae, 200)
    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth,
        environment_map=environment_map
    ).renderRayTrace(output_file)

