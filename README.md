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

Args:

`-m` `--method_name` Expected method names: raytracing, pathtracing, photon_mapping
`-f` `--file_dae_path`
`-e` `--environment_map_path`
`-r` `--resolution`, required=False, default=200
`-s` `--samples`, required=False, default=1
`-d` `--max_depth`, required=False, default=3
`-p` `--n_photons`, required=False, default=50000
`-o` `--output_file`, required=False, default=out.png

  

```
python src/main.py -m photon_mapping -f src/scenes/path_tracing_scene.dae -e src/scenes/skbx.jpg
```
