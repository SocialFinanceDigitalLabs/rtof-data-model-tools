#!/usr/bin/env python

import argparse

from jinja2 import Environment, select_autoescape, FileSystemLoader

from rtofdata.config import assets_dir, output_dir
from rtofdata.specification.spec_parser import parse_specification
from rtofdata.word import create_context


def main(filename):
    spec = parse_specification()
    context = create_context(spec)
    env = Environment(
        loader=FileSystemLoader(assets_dir / "examples"),
        autoescape=select_autoescape()
    )
    template = env.get_template(filename)
    output_filename = output_dir / filename
    with open(output_filename, "wt") as file:
        file.write(template.render(context))
    print(f"Wrote output to {output_filename.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process the RTOF data specification'
    )
    parser.add_argument('filename', type=str, help='The filename to read')

    args = parser.parse_args()

    main(args.filename)