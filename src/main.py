import argparse

from typing import Optional, Sequence

from procedure import MainProcedure


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--method_name")
    parser.add_argument("-f", "--file_dae_path")
    parser.add_argument("-e", "--environment_map_path")
    parser.add_argument("-r", "--resolution", required=False, default=200)
    parser.add_argument("-s", "--samples", required=False, default=1)
    parser.add_argument("-d", "--max_depth", required=False, default=3)
    parser.add_argument("-p", "--n_photons", required=False, default=50000)
    parser.add_argument("-o", "--output_file", required=False, default="out.png")

    args = parser.parse_args(argv)

    render_procedure = MainProcedure(
        method_name=args.method_name,
        scene_file=args.file_dae_path,
        resolution=int(args.resolution),
        samples=int(args.samples),
        max_depth=int(args.max_depth),
        environment_map=args.environment_map_path,
        n_photons=int(args.n_photons),
        output_file=args.output_file,
    )

    render_procedure.render()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
