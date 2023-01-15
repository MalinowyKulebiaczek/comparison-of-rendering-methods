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