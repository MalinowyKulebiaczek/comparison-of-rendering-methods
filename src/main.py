import argparse

from typing import Optional, Sequence

from procedure import MainProcedure


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="comparison-of-rendering-methods",
        description="Program allows rendering by various methods",
        epilog="Example usage: python src/main.py photon_mapping src/scenes/path_tracing_scene.dae src/scenes/skbx.jpg -o output.png",
    )
    parser.add_argument(
        "method_name",
        help="Expected method names: raytracing, pathtracing, photon_mapping",
    )
    parser.add_argument("file_dae_path", help="Path to dae file")
    parser.add_argument("environment_map_path", help="Path to environment map image")
    parser.add_argument(
        "-r",
        "--resolution",
        required=False,
        type=int,
        default=200,
        help="Scene and camera resolution",
    )
    parser.add_argument(
        "-s", "--samples", required=False, type=int, default=1, help="Number of samples"
    )
    parser.add_argument(
        "-d", "--max_depth", required=False, type=int, default=3, help="Maximum depth"
    )
    parser.add_argument(
        "-p",
        "--n_photons",
        required=False,
        type=int,
        default=50000,
        help="Number of photons to shot in photon_mapping",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        required=False,
        default="out.png",
        help="Output file path",
    )

    args = parser.parse_args(argv)

    render_procedure = MainProcedure(
        method_name=args.method_name,
        scene_file=args.file_dae_path,
        resolution=args.resolution,
        samples=args.samples,
        max_depth=args.max_depth,
        environment_map=args.environment_map_path,
        n_photons=args.n_photons,
        output_file=args.output_file,
    )

    render_procedure.render()
    render_procedure.display_statistics()
    render_procedure.save_statistics()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
