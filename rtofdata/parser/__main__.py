import argparse
from dataclasses import asdict
from pathlib import Path

import yaml

from rtofdata.config import output_dir as conf_output_dir
from rtofdata.parser import Parser
from rtofdata.specification.parser import parse_specification


def dict_factory(obj):
    my_dict = {}
    for (k, v) in obj:
        if v is None:
            continue
        if hasattr(v, "_make"):
            v = v._asdict()
            del v['record']
        my_dict[k] = v
    return my_dict


def main(input_files, output_dir=None):
    spec = parse_specification()

    if not output_dir:
        output_dir = conf_output_dir / "eventstream"
    elif isinstance(output_dir, str):
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    parser = Parser(spec)
    for filename in input_files:
        print(f"Processing {filename}", end="\r")

        infile = Path(filename)
        data = parser.parse_file(infile)
        outfile = output_dir / f"{infile.stem}.yml"
        print(f"Preparing output from {filename}", end="\r")
        with open(outfile, "wt") as file:
            yaml.dump([asdict(d, dict_factory=dict_factory) for d in data], file, sort_keys=False)
        print(f"Processed {filename} to {outfile.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse RTOF data files'
    )
    parser.add_argument("filename", type=str, nargs="+")
    parser.add_argument("--output-dir", "-o", type=str, nargs="?", help="Write output to this directory")
    args = parser.parse_args()

    main(args.filename, output_dir=args.output_dir)
