# TRAK- Project

comparison-of-rendering-methods

## Team

Damian Łysomirski

Rafał Wiercioch

Maciej Kapuściński

Robert Kaczmarski

  

## Downloading and instalation

```
# Clone repo
git clone https://github.com/MalinowyKulebiaczek/comparison-of-rendering-methods.git
cd comparison-of-rendering-methods 

# Creating virtual environment
python -m venv venv 
source ./venv/bin/activate

# Installing requirements
pip install -r requirements.txt
``` 

## Parameter description and example of program usage

Positional arguments:
  `method_name `          Expected method names: raytracing, pathtracing, photon_mapping
  `file_dae_path`         Path to dae file
  `environment_map_path`  Path to environment map image

Optional arguments:
 `-h` `--help`          Show help message
 
`-m`  `--method_name` Expected method names: raytracing, pathtracing, photon_mapping

`-f`  `--file_dae_path` Path to dae file

`-e`  `--environment_map_path` Path to environment map image

`-r`  `--resolution` Scene and camera resolution, required=False, default=200 

`-s`  `--samples`Number of samples, required=False, default=1

`-d`  `--max_depth` Maximum depth, required=False, default=3

`-p`  `--n_photons` Number of photons to shot in photon_mapping, required=False, default=50000

`-o`  `--output_file`Output file path, required=False, default=out.png

## Example usage
```
python src/main.py photon_mapping src/scenes/path_tracing_scene.dae src/scenes/skbx.jpg -o output.png

```

## Results
### Renders
All renders were done with default parameters, which are:
- Path tracing
    - samples: 1
    - max depth: 3
- Photon Mapping:
    - number of photons: 50000
    - max depth: 3

#### Scene called "path_tracing_scene2"
##### Path Tracing
![Alt text](results/png/scene_1_cube_rendered_with_pathtracing.png?raw=true "Title") 
##### Ray Tracing
![Alt text](results/png/scene_1_cube_rendered_with_raytracing.png?raw=true "Title") 
##### Photon Mapping
![Alt text](results/png/scene_1_cube_rendered_with_photon_mapping.png?raw=true "Title")


#### Scene called "path_tracing_scene"
##### Path Tracing
![Alt text](results/png/path_tracing_scene_rendered_with_pathtracing.png?raw=true "Title") 

##### Ray Tracing
![Alt text](results/png/path_tracing_scene_rendered_with_raytracing.png?raw=true "Title")

##### Photon Mapping
![Alt text](results/png/path_tracing_scene_rendered_with_photon_mapping.png?raw=true "Title")

### Plots
![Alt text](results/plots/intersections_in_relation_to_triangles.png?raw=true "Title")

![Alt text](results/plots/times_in_relation_to_triangles.png?raw=true "Title")
