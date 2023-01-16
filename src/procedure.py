from scenecomponents.background import Background
from scenecomponents.scene import Scene


class MainProcedure:
    """
    This class represents
    procedure configuration,
    input resources parsing and
    execution of path tracing
    algorithm.
    """

    def __init__(
        self,
        method_name: str,
        scene_file: str,
        resolution: int,
        samples: int,
        max_depth: int,
        environment_map: str,
        n_photons: int,
        output_file: str,
    ):
        """
        Load configuration
        """
        self.method_name = method_name
        self.scene_file = scene_file
        self.resolution = resolution
        self.background_color = None
        self.environment_map = environment_map
        self.scene = None
        self.background = None
        self.samples = samples
        self.max_depth = max_depth
        self.n_photons = n_photons
        self.output_file = output_file
        self.statistics = {}

    def load_scene(self):
        self.scene = Scene.load(self.scene_file, self.resolution)

    def free_scene(self):
        self.scene = None

    def renderPathTrace(self) -> None:
        """
        Run path tracing render
        """
        from renders.pathtracing.pathtrace import path_trace

        print("Started rendering. Please wait...")
        image = path_trace(self)
        print("Done!")
        image.show()
        image.save(self.output_file)

    def renderRayTrace(self) -> None:
        """
        Run ray tracing render
        """
        from renders.raytracing.raytracing_scene_load import ray_tracing_render

        print("Started rendering. Please wait...")
        image = ray_tracing_render(self, self.max_depth)
        print("Done!")
        image.show()
        image.save(self.output_file)

    def renderPhotonMap(self) -> None:
        """
        Run photon mapping render
        """
        from renders.photon_mapping.photon_mapping import render_photon_mapping

        print("Started rendering. Please wait...")
        image = render_photon_mapping(self, self.n_photons, self.max_depth)
        print("Done!")
        image.show()
        image.save(self.output_file)

    def load_background(self):
        self.background = Background(self.background_color, self.environment_map)
        
    def display_statistics(self):
        print(f"Statistics for {self.method_name} method:")
        for key, value in self.statistics.items():
            print(f"{key}: {value}")

    def render(self):
        if self.method_name == "raytracing":
            self.renderRayTrace()
        elif self.method_name == "pathtracing":
            self.renderPathTrace()
        elif self.method_name == "photon_mapping":
            self.renderPhotonMap()
        else:
            raise ValueError(
                f"Method name {self.method_name} is not supported. Expected method names: raytracing, pathtracing, photon_mapping."
            )
