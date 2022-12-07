from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == '__main__':
    file_dae = "src/scenes/test2.dae"
    resolution = 400
    samples = 64
    max_depth = 3

    scene = Scene.load(file_dae, 400)
    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth
    ).render(output_file)

