import argparse
from pathlib import Path

import tablib
from sqlalchemy import create_engine

from rtofdata.config import output_dir
from rtofdata.fake.faker import create_all_data
from rtofdata.fake.serialization import dataset_to_tablib, dataset_to_wide
from rtofdata.fake.sql import create_schema, insert_into_database, get_orm_mappings, database_to_wide
from rtofdata.spec_parser import parse_specification

parser = argparse.ArgumentParser(
    description='Create fake data'
)
parser.add_argument("config_file", type=str, nargs='?', help="The sample input generator")
parser.add_argument("-n", "--number", type=int, nargs='?', help="The number of top-level records to generate")
args = parser.parse_args()

spec = parse_specification()

metadata_obj = create_schema(spec)

generated = create_all_data(spec=spec, config_file=args.config_file, num=args.number, progress=True)

tabular = dataset_to_tablib(generated, spec)
book = tablib.Databook(tabular)

name_root = "samples/sample"

Path(output_dir / name_root).parent.mkdir(parents=True, exist_ok=True)

with open(output_dir / f"{name_root}.xlsx", "wb") as file:
    file.write(book.export('xlsx'))

for table in tabular:
    with open(output_dir / f"{name_root}_record_{table.title}.csv", "wt") as file:
        file.write(table.export('csv'))

sql_database = Path(output_dir / "samples/sqlite.db")
sql_database.unlink(missing_ok=True)
engine = create_engine(f'sqlite:///{sql_database.absolute()}')
metadata_obj.create_all(engine)
insert_into_database(engine, metadata_obj, generated)

data = database_to_wide(engine, spec)
with open(output_dir / f"{name_root}_wide.csv", "wt") as file:
    file.write(data.export("csv"))


with open(output_dir / f"{name_root}.yml", "wt") as file:
    file.write(book.export('yaml'))