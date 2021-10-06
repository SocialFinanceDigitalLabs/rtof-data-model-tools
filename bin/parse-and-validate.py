import argparse
from pathlib import Path

import tablib

from rtofdata.datasource.in_memory import InMemoryDataSource
from rtofdata.fake.serialization import dataset_to_tablib
from rtofdata.parser import Parser
from rtofdata.specification.parser import parse_specification
from rtofdata.validation import Validator


def main(input_file_list):

    spec = parse_specification()

    parser = Parser(spec)
    datasource = InMemoryDataSource(spec)
    for filename in input_file_list:
        print(f"Processing {filename}", end="\r")

        infile = Path(filename)
        event_stream = parser.parse_file(infile)
        for event in event_stream:
            datasource.update(event)
            # stream.process_event(asdict(event))

        validator = Validator(spec, datasource)
        validator.validate_all()

        by_record = {s.id: {r: datasource.get_single_record(s.id, *r)._asdict() for r in datasource.get_records_by_type(s.id)} for s in spec.records}

        tabular = dataset_to_tablib(by_record, spec)

        book = tablib.Databook(tabular)
        with open("output/parsed.xlsx", "wb") as file:
            file.write(book.export('xlsx'))

        # with open(outfile, "wt") as file:
        #     yaml.dump([asdict(d, dict_factory=dict_factory) for d in data], file, sort_keys=False)
        # print(f"Processed {filename} to {outfile.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Upload a file to the publish webhook'
    )
    parser.add_argument("input_files", type=str, nargs="+", help="The input file(s)")
    args = parser.parse_args()
    main(args.input_files)