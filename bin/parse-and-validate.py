import argparse
from pathlib import Path
from datetime import datetime
from random import SystemRandom

from pytz import timezone
from time import strftime

import tablib
from sqlalchemy import create_engine

from rtofdata.datasource.in_memory import InMemoryDataSource
from rtofdata.fake.serialization import dataset_to_tablib
from rtofdata.fake.sql import create_schema, insert_into_database, database_to_wide
from rtofdata.parser import Parser
from rtofdata.specification.parser import parse_specification
from rtofdata.util.error_handler import ErrorEvent
from rtofdata.validation import Validator

TZ = timezone('Europe/London')
random = SystemRandom()


class FileErrorHandler:

    def __init__(self):
        self.events = []

    def __call__(self, event: ErrorEvent):
        self.events.append(event)


def main(team_channel_folder, export_database=False):
    team_channel_folder = Path(team_channel_folder)
    upload_folder = team_channel_folder / "Upload"
    reports_folder = team_channel_folder / "Reports"
    data_folder = team_channel_folder / "Data"
    archive_folder = team_channel_folder / "Archive"

    timestamp = datetime.now(TZ).strftime("%Y%m%dT%H%M%S-") + str(random.randint(1000,9999))
    year_month = datetime.now(TZ).strftime("%Y-%m")

    error_handler = FileErrorHandler()

    spec = parse_specification()

    parser = Parser(spec, error_handler=error_handler)
    datasource = InMemoryDataSource(spec)

    files_to_process = []
    for filename in upload_folder.glob("*"):
        if filename.suffix in ['.csv', '.xlsx']:
            files_to_process.append(filename)

    if len(files_to_process) == 0:
        print("No files found")
        exit(0)

    for filename in files_to_process:
        event_stream = parser.parse_file(filename)
        for event in event_stream:
            datasource.update(event)

    validator = Validator(spec, datasource, error_handler=error_handler)
    validator.validate_all()

    by_record = {s.id: {r: datasource.get_single_record(s.id, *r)._asdict() for r in datasource.get_records_by_type(s.id)} for s in spec.records}
    tabular = dataset_to_tablib(by_record, spec)
    book = tablib.Databook(tabular)

    (data_folder / year_month).mkdir(parents=True, exist_ok=True)
    with open(data_folder / year_month / f"{timestamp}-data.xlsx", "wb") as file:
        file.write(book.export('xlsx'))

    if export_database:
        sql_database = Path(data_folder / year_month / f"{timestamp}.sqlite")
        sql_database.unlink(missing_ok=True)
        engine = create_engine(f'sqlite:///{sql_database.absolute()}')
        metadata_obj = create_schema(spec)
        metadata_obj.create_all(engine)
        insert_into_database(engine, metadata_obj, by_record)
        data = database_to_wide(engine, spec)
        with open(data_folder / year_month / f"{timestamp}-wide.xlsx", "wb") as file:
            file.write(data.export("xlsx"))

    headers = []
    for e in error_handler.events:
        for k in e.keys():
            if k not in headers:
                headers.append(k)

    data = tablib.Dataset(headers=headers)
    for e in error_handler.events:
        data.append([e.get(h) for h in headers])

    (reports_folder / year_month).mkdir(parents=True, exist_ok=True)
    with open(reports_folder / year_month / f"{timestamp}-validation.xlsx", "wb") as file:
        file.write(data.export("xlsx"))

    report_data = tablib.Dataset()
    for ix, e in enumerate(error_handler.events):
        if ix > 0:
            report_data.append(("--", ""))
        for k, v in e.items():
            report_data.append((f"{k}:", v))

    with open(reports_folder / year_month / f"{timestamp}-validation.txt", "w") as file:
        file.write(report_data.export("cli"))

    (archive_folder / year_month / timestamp).mkdir(parents=True, exist_ok=True)
    for filename in files_to_process:
        filename.rename(archive_folder / year_month / timestamp / filename.name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Upload a file to the publish webhook'
    )
    parser.add_argument("team_channel_folder", type=str, help="The input channel folder")
    args = parser.parse_args()
    main(args.team_channel_folder)