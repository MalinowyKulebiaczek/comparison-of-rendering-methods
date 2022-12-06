from procedure import MainProcedure
from scenecomponents.scene import Scene

if __name__ == '__main__':
    file_dae = "../resources/scenes/test2.dae"
    resolution = 200
    samples = 20
    max_depth = 20

    scene = Scene.load(file_dae, 200)
    output_file = "out.png"

    MainProcedure(
        scene_file=file_dae,
        resolution=resolution,
        samples=samples,
        max_depth=max_depth
    ).render(output_file)
