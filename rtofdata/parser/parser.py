from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Any, Dict, Tuple, Union

import dateutil.parser
import tablib

from rtofdata.parser import fix_field_id, file_to_databook, file_to_digest, pick_value
from rtofdata.specification.data import Specification, Field, Record
from rtofdata.util.error_handler import ErrorEvent, print_error_handler as default_error_handler


@dataclass
class DataEvent:
    field: str
    record: str
    value: Any
    primary_key: Any = None
    suffix: str = None
    row: int = None
    column: int = None
    sheet: str = None
    filename: str = None
    file_sha512: str = None


def default_error_handler(event: ErrorEvent):
    print(event)


class Parser:
    def __init__(self, spec: Specification):
        self.__spec = spec
        self.__all_fields = [(fix_field_id(f.field.id), f) for f in spec.fields if not f.field.foreign_keys]

    def parse_file(self, filename: Path, error_handler=None) -> List:
        databook = file_to_databook(filename)
        digest = file_to_digest(filename)
        return self.databook_to_events(databook, filename=filename.name, digest=digest, error_handler=error_handler)

    def get_by_field_id(self, field_id) -> Union[Tuple[Field, str], None]:
        field_id = fix_field_id(field_id)
        if field_id is None:
            return None
        for fid, field in self.__all_fields:
            if field_id.startswith(fid):
                return field, field_id[len(fid):]

    def databook_to_events(self, databook, filename=None, digest=None, error_handler=None):
        parsed_data = []
        for dataset in databook.sheets():
            parsed_data += self.dataset_to_events(dataset, filename=filename, digest=digest, error_handler=error_handler)
        return parsed_data

    def dataset_to_events(self, dataset: tablib.Dataset, filename=None, digest=None, error_handler=None):
        if error_handler is None:
            error_handler = default_error_handler
        fields = [self.get_by_field_id(h) for h in dataset.headers]
        for ix, f in enumerate(fields):
            if f is None:
                error_handler(ErrorEvent(
                    message=f"Header not found {dataset.headers[ix]}",
                    filename=filename,
                    digest=digest
                ))

        parsed_data: List[DataEvent] = []
        for row_ix, row in enumerate(dataset):
            row_data = self.row_to_events(row_ix, row, fields, filename=filename, digest=digest)
            row_data = self.filter_empty_suffixes(row_data)

            row_keys = self.keys_in_row(row_data)

            row_data = self.add_pk_to_events(row_data, row_keys)

            if not self.is_row_empty(row_data):
                parsed_data += row_data

        return parsed_data

    @staticmethod
    def row_to_events(row_ix: int, row: List, fields: List, filename=None, digest=None, sheet=None):
        """
        Returns a list of 'raw' events as seen in the Row - these are not aware of other events in the row, but simply
        processes column by column.
        :return:
        """
        row_data: List[DataEvent] = []
        for ix, f in enumerate(fields):
            if f is None:  # We encountered an unknown field, so we skip column
                continue
            field_and_record, suffix = f

            value = row[ix]
            field_type = field_and_record.field.type
            if field_type.id == "date" and isinstance(value, str):
                value = dateutil.parser.isoparse(value)

            event = DataEvent(
                field=field_and_record.field.id,
                record=field_and_record.record.id,
                value=value,
                suffix=suffix,
                sheet=sheet,
                row=row_ix,
                column=ix,
                filename=filename,
                file_sha512=digest,
            )
            row_data.append(event)
        return row_data

    def keys_in_row(self, row_data) -> Dict[Tuple[str, str], Tuple]:
        # To resolve primary keys for each column, we need to
        # check if we have values for each record's keys
        records_in_row = {(e.record, e.suffix): self.__spec.record_by_id(e.record) for e in row_data}
        keys_in_row: Dict[Tuple[str, str], Tuple] = {}
        for (record_id, suffix), record in records_in_row.items():
            key_values = {}
            for key in record.primary_keys:
                if key.foreign_keys:
                    for fk in key.foreign_keys:
                        key_values[key.id] = pick_value(row_data, field=fk['field'], record=fk['record'])
                else:
                    key_val = pick_value(row_data, field=key.id, suffix=suffix)
                    key_values[key.id] = key_val

            keys_in_row[(record_id, suffix)] = record.get_key(**key_values)
        return keys_in_row

    def add_pk_to_events(self, row_data, keys_in_row):
        row_data = [DataEvent(**asdict(e)) for e in row_data]
        for event in row_data:
            record = self.__spec.record_by_id(event.record)
            field = record.field_by_id(event.field)
            if not field.primary_key:
                event.primary_key = keys_in_row[(event.record, event.suffix)]

        return [e for e in row_data if e.primary_key]

    @staticmethod
    def is_row_empty(row_data: List[DataEvent]):
        row_values = [e.value for e in row_data if e.value != '']
        return len(row_values) == 0

    @staticmethod
    def filter_empty_suffixes(row_data: List[DataEvent]):
        group_by_suffix = {}
        for event in row_data:
            group_by_suffix.setdefault(event.suffix, []).append(event)

        values_by_suffix = {suffix: [e.value for e in events] for suffix, events in group_by_suffix.items()}
        values_by_suffix = {suffix: "".join([str(v) for v in values]) for suffix, values in values_by_suffix.items()}

        # We do it this way to preserve the order of events
        filtered_values = list(row_data)
        for suffix, value in values_by_suffix.items():
            if len(value) == 0:
                for v in group_by_suffix[suffix]:
                    filtered_values.remove(v)

        return filtered_values
