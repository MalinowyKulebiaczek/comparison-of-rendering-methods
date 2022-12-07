from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == '__main__':
    file_dae = "src/scenes/test2.dae"
    resolution = 200
    samples = 8
    max_depth = 1
    environment_map="src/scenes/env.jpg"

    scene = Scene.load(file_dae, 200)
    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth,
        environment_map=environment_map
    ).render(output_file)

