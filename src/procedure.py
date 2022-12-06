from scenecomponents.background import Background
from scenecomponents.scene import Scene


class MainProcedure:
    """
    This class represents
    procedure configuration,
    input resources parsing and
    execution of path tracing
    algorithm.

    Created object stores all
    local resources:
        - scene
        - sampler object
        - environment map
        - camera information
    """

    def __init__(
            self,
            scene_file: str,
            resolution: int,
            samples: int,
            max_depth: int
    ):
        """
        Load configuration
        """
        self.scene_file = scene_file
        self.resolution = resolution
        self.background_color = None
        self.environment_map = None
        self.scene = None
        self.background = None
        self.samples = samples
        self.max_depth = max_depth

    def load_scene(self):
        self.scene = Scene.load(self.scene_file, self.resolution)

    def free_scene(self):
        self.scene = None

    def render(self, output_file) -> None:
        """
        Run path tracing render
        """
        from renders.pathtracing.pathtrace import path_trace

        print("Started rendering. Please wait...")
        image = path_trace(self)
        print("Done!")
        image.show()
        image.save(output_file)

    def load_background(self):
        self.background = Background(self.background_color, self.environment_map)
