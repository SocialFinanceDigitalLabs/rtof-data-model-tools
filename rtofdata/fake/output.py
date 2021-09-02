from pathlib import Path

import tablib
from sqlalchemy import create_engine

from rtofdata.fake.faker import create_all_data
from rtofdata.fake.serialization import dataset_to_tablib
from rtofdata.fake.sql import create_schema, insert_into_database, database_to_wide
from rtofdata.specification.parser import parse_specification
from rtofdata.config import output_dir


def write_samples(
        config_file,
        sample_output=output_dir / "samples",
        sample_root="sample",
        num=None,
        write_xlsx=True,
        write_csv_individual=True,
        write_csv_wide=True,
        write_sqlite=True,
        progress=True,
):
    sample_output.mkdir(parents=True, exist_ok=True)

    spec = parse_specification()

    generated = create_all_data(spec=spec, config_file=config_file, num=num, progress=progress)
    tabular = dataset_to_tablib(generated, spec)

    if write_xlsx:
        book = tablib.Databook(tabular)
        with open(sample_output / f"{sample_root}.xlsx", "wb") as file:
            file.write(book.export('xlsx'))

    if write_csv_individual:
        for table in tabular:
            with open(sample_output / f"{sample_root}_record_{table.title}.csv", "wt") as file:
                file.write(table.export('csv'))

    if write_sqlite:
        sql_database = Path(sample_output / f"{sample_root}.sqlite")
        sql_database.unlink(missing_ok=True)
        engine = create_engine(f'sqlite:///{sql_database.absolute()}')
    elif write_csv_wide:
        engine = create_engine(':memory:')
    else:
        engine = None

    if engine is not None:
        metadata_obj = create_schema(spec)
        metadata_obj.create_all(engine)
        insert_into_database(engine, metadata_obj, generated)

    if write_csv_wide:
        data = database_to_wide(engine, spec)
        with open(sample_output / f"{sample_root}_wide.csv", "wt") as file:
            file.write(data.export("csv"))
