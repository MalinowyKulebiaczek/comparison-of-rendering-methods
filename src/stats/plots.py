import matplotlib.pyplot as plt
from statutilities import StatisticsUtilities


class RenderStatistics:

    def __init__(self, render_method, num_of_triangles: list[int], times: list[int], num_of_intersections: list[int],
                 additional_info: dict = None):
        self.render_method = render_method
        self.num_of_triangles = num_of_triangles
        self.times = times  # in seconds!
        self.num_of_intersections = num_of_intersections
        self.additional_info = additional_info

    def prepare_label(self):
        label = self.render_method
        if self.additional_info is not None:
            label += " ("
            for key, value in self.additional_info.items():
                label += key + "=" + value + ", "
            label = label[:len(label) - 2]
            label += ")"
        return label


class Plotter:
    @staticmethod
    def plot_times_in_relation_to_triangles(infos: list[RenderStatistics]):
        for info in infos:
            plt.plot(info.num_of_triangles, info.times, label=info.prepare_label(), marker="o")
        plt.legend()
        plt.title("Comparison of rendering methods: Time")
        plt.ylabel("Time [s]")
        plt.xlabel("Number of triangles")
        plt.savefig("../" + StatisticsUtilities.RESULT_DIRECTORY + StatisticsUtilities.PLOT_DIRECTORY
                    + "times_in_relation_to_triangles.png")
        plt.show()

    @staticmethod
    def plot_intersections_in_relation_to_triangles(infos: list[RenderStatistics]):
        for info in infos:
            plt.plot(info.num_of_triangles, info.num_of_intersections, label=info.prepare_label(), marker="o")
        plt.legend()
        plt.title("Comparison of rendering methods: Intersections")
        plt.ylabel("Number of intersections")
        plt.xlabel("Number of triangles")
        plt.savefig(
            "../" + StatisticsUtilities.RESULT_DIRECTORY + StatisticsUtilities.PLOT_DIRECTORY
            + "intersections_in_relation_to_triangles.png")
        plt.show()


if __name__ == "__main__":
    number_of_triangles = [12,  # scene_1_cube.dae
                           34,  # scene_walls_cubes.dae
                           994,  # path_tracing_scene.dae
                           1920]  # path_tracing_scene2.dae
    pathTraceInfo = RenderStatistics(
        render_method="Path Tracing",
        num_of_triangles=number_of_triangles,
        times=[18, 44, 131, 83],
        num_of_intersections=[2491, 189130, 185739, 3448],
        additional_info={"samples": "1", "max depth": "3"}
    )

    rayTraceInfo = RenderStatistics(
        render_method="Ray Tracing",
        num_of_triangles=number_of_triangles,
        num_of_intersections=[2491, 68515, 68515, 3424],
        times=[19, 22, 67, 69]
    )

    photonMappingInfo = RenderStatistics(
        render_method="Photon Mapping",
        num_of_triangles=number_of_triangles[:-1],  # without the last scene becasue the render took too long
        times=[113, 66, 177],
        num_of_intersections=[121000, 122853, 124215],
        additional_info={"photons": "50000", "max depth": "3"}
    )

    Plotter.plot_times_in_relation_to_triangles([rayTraceInfo, pathTraceInfo, photonMappingInfo])
    Plotter.plot_intersections_in_relation_to_triangles([rayTraceInfo, pathTraceInfo, photonMappingInfo])
