from scenecomponents.background import Background
from scenecomponents.scene import Scene
import os.path

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
        
    def save_image_to_results(self, image):
        """
        Aded some code to archiving results
        """
        i = 0
        path = "wyniki/Figure_1" + "_" + str(self.method_name) + ".png"
        while os.path.exists(path):
            i = i +1
            new_path = "wyniki/Figure_" + str(i) + "_" + str(self.method_name) + ".png"
            path = new_path
        else:
            image.save(path)

    def check_path_for_results(self):
        """
        Aded some code to check path to archive statistics
        """
        i = 0
        path = "wyniki/Figure_1" + "_" + str(self.method_name) + ".txt"
        while os.path.exists(path):
            i = i +1
            new_path = "wyniki/Figure_" + str(i) + "_" + str(self.method_name) + ".txt"
            path = new_path
        else:
            return path

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

        #To store in archive
        self.save_image_to_results(image)

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

        #To store in archive
        self.save_image_to_results(image)

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

        #To store in archive
        self.save_image_to_results(image)

    def load_background(self):
        self.background = Background(self.background_color, self.environment_map)

    def set_statistic(self, key, value):
        self.statistics[key] = value

    def display_statistics(self):
        print(f"Statistics for {self.method_name} method:")
        for key, value in self.statistics.items():
            print(f"{key}: {value}")
        #Aded some render parameters to statistics display
        print(f"Scene file: {self.scene_file}")
        print(f"Environment map file: {self.environment_map}")
        print(f"Resolution: {self.resolution}")
        print(f"Max_depth: {self.max_depth}")
        if self.method_name == "raytracing":
            pass
        elif self.method_name == "pathtracing":
            print(f"Samples: {self.samples}")
        elif self.method_name == "photon_mapping":
            print(f"Number of photons:: {self.n_photons}")

    def save_statistics(self):
        path = str(self.check_path_for_results())
        with open(path, 'w+') as file:
            print(f"Statistics for {self.method_name} method:", file=file)
            for key, value in self.statistics.items():
                print(f"{key}: {value}",file=file)
            #Aded some render parameters to statistics display
            print(f"Scene file: {self.scene_file}",file=file)
            print(f"Environment map file: {self.environment_map}",file=file)
            print(f"Resolution: {self.resolution}",file=file)
            print(f"Max_depth: {self.max_depth}",file=file)
            if self.method_name == "raytracing":
                pass
            elif self.method_name == "pathtracing":
                print(f"Samples: {self.samples}",file=file)
            elif self.method_name == "photon_mapping":
                print(f"Number of photons:: {self.n_photons}",file=file)


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
