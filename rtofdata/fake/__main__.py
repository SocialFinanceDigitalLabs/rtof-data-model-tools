import os
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create fake data'
    )
    parser.add_argument("config_file", type=str, nargs='?', help="The sample input generator")
    parser.add_argument("-n", "--number", type=int, nargs='?', help="The number of top-level records to generate")
    parser.add_argument("-o", "--output", type=str, nargs='?', help="The output folder")
    parser.add_argument("-r", "--root", type=str, nargs='?', help="The output filename root")
    parser.add_argument("-d", "--data-dir", type=str, nargs="?", help="Location of RTOF data repository")

    args = parser.parse_args()

    if args.data_dir:
        os.environ["DATA_ROOT"] = args.data_dir

    kwargs = {}
    if args.output:
        kwargs['sample_output'] = args.output
    if args.root:
        kwargs['sample_root'] = args.root
    if args.number:
        kwargs['num'] = args.number

    # We do this after the DATA_ROOT has been configured
    from .output import write_samples
    write_samples(args.config_file, **kwargs)


