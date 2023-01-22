import os


class StatisticsUtilities:
    RESULT_DIRECTORY = "./results"  # if No Such File or Directory error occurs then try deleting "../"
    PNG_DIRECTORY = "/png/"
    TXT_DIRECTORY = "/txt/"
    PLOT_DIRECTORY = "/plots/"

    @staticmethod
    def prepare_result_filename(scene_file, method_name, subdirectory, number_of_file=None):
        scene_name = scene_file.split("/")[-1].split(".")[0]
        output_file_name = StatisticsUtilities.RESULT_DIRECTORY + subdirectory + scene_name + "_rendered_with_" + str(method_name)
        if number_of_file is not None:
            output_file_name = output_file_name + str(number_of_file)
        return output_file_name

    @staticmethod
    def save_image_to_results(scene_file, method_name, image):
        """
        Aded some code to archiving results
        """
        i = 0
        path = StatisticsUtilities.prepare_result_filename(scene_file, method_name,
                                                           StatisticsUtilities.PNG_DIRECTORY) + ".png"
        while os.path.exists(path):
            i = i + 1
            new_path = StatisticsUtilities.prepare_result_filename(scene_file, method_name,
                                                                   StatisticsUtilities.PNG_DIRECTORY, i) + ".png"
            path = new_path
        else:
            image.save(path)

    @staticmethod
    def check_path_for_results(scene_file, method_name):
        """
        Aded some code to check path to archive statistics
        """
        i = 0
        path = StatisticsUtilities.prepare_result_filename(scene_file, method_name,
                                                           StatisticsUtilities.TXT_DIRECTORY) + ".txt"
        while os.path.exists(path):
            i = i + 1
            new_path = StatisticsUtilities.prepare_result_filename(scene_file, method_name,
                                                                   StatisticsUtilities.TXT_DIRECTORY, i) + ".txt"
            path = new_path
        else:
            return path

    @staticmethod
    def display_statistics(render_procedure):
        print(f"Statistics for {render_procedure.method_name} method:")
        for key, value in render_procedure.statistics.items():
            print(f"{key}: {value}")
        # Aded some render parameters to statistics display
        print(f"Scene file: {render_procedure.scene_file}")
        print(f"Environment map file: {render_procedure.environment_map}")
        print(f"Resolution: {render_procedure.resolution}")
        print(f"Max_depth: {render_procedure.max_depth}")
        if render_procedure.method_name == "raytracing":
            pass
        elif render_procedure.method_name == "pathtracing":
            print(f"Samples: {render_procedure.samples}")
        elif render_procedure.method_name == "photon_mapping":
            print(f"Number of photons: {render_procedure.n_photons}")

    @staticmethod
    def save_statistics(render_procedure):
        path = str(StatisticsUtilities.check_path_for_results(render_procedure.scene_file, render_procedure.method_name))
        with open(path, 'w+') as file:
            print(f"Statistics for {render_procedure.method_name} method:", file=file)
            for key, value in render_procedure.statistics.items():
                print(f"{key}: {value}", file=file)
            # Added some render parameters to statistics display
            print(f"Scene file: {render_procedure.scene_file}", file=file)
            print(f"Environment map file: {render_procedure.environment_map}", file=file)
            print(f"Resolution: {render_procedure.resolution}", file=file)
            print(f"Max_depth: {render_procedure.max_depth}", file=file)
            if render_procedure.method_name == "raytracing":
                pass
            elif render_procedure.method_name == "pathtracing":
                print(f"Samples: {render_procedure.samples}", file=file)
            elif render_procedure.method_name == "photon_mapping":
                print(f"Number of photons: {render_procedure.n_photons}", file=file)
