#!/usr/bin/env python

import argparse
import os


def main(data_dir=None):
    if data_dir:
        os.environ["DATA_ROOT"] = data_dir

    from rtofdata.erd import create_erd
    from rtofdata.excel import write_excel_specification
    from rtofdata.jekyll import write_jekyll_specification
    from rtofdata.spec_parser import parse_specification
    from rtofdata.word import write_word_specification

    spec = parse_specification()

    create_erd(spec)
    write_word_specification(spec)
    write_excel_specification(spec)
    write_jekyll_specification(spec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process the RTOF data specification'
    )

    parser.add_argument("--data-dir", "-d", type=str, nargs="?", help="Location of RTOF data repository")
    args = parser.parse_args()

    main(data_dir=args.data_dir)
