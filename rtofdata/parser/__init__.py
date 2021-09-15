import hashlib
import re
from pathlib import Path
from typing import List

import tablib

from rtofdata.specification.data import Specification


def _pick_value(row_data, **kwargs):
    def _matches(c):
        for key, value in kwargs.items():
            if c.get(key) != value:
                return False
        return True

    matches = [c['value'] for c in row_data if _matches(c)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    else:
        raise ValueError(f"Multiple matches found: {matches}")


class Parser:
    __ptn_field_id = re.compile(r"[^a-z0-9]")

    def __init__(self, spec: Specification):
        self.__spec = spec
        self.__all_fields = [(self._fix_field_id(f.field.id), f) for f in spec.fields if not f.field.foreign_keys]

    def _fix_field_id(self, field_id):
        if field_id is None:
            return None
        return self.__ptn_field_id.sub("", field_id.lower())

    def get_by_field_id(self, field_id):
        field_id = self._fix_field_id(field_id)
        for fid, field in self.__all_fields:
            if field_id.startswith(fid):
                return field, field_id[len(fid):]

    def parse_file(self, filename: Path) -> List:
        if filename.suffix == ".csv":
            with open(filename, 'rt') as fh:
                dataset = tablib.Dataset().load(fh, format="csv")
                databook = tablib.Databook([dataset])
        elif filename.suffix == ".xlsx":
            with open(filename, 'rb') as fh:
                databook = tablib.Databook().load(fh, format="xlsx")
        else:
            raise Exception(f"Unknown file type: {filename}")

        with open(filename, 'rb') as fh:
            digest = hashlib.sha512(fh.read())
        digest = digest.hexdigest()

        parsed_data = []
        for dataset in databook.sheets():
            fields = [self.get_by_field_id(h) for h in dataset.headers]
            for ix, f in enumerate(fields):
                if f is None:
                    print("Header not found:", dataset.headers[ix])

            for row_ix, row in enumerate(dataset):
                row_data = []
                for ix, f in enumerate(fields):
                    if f is not None:
                        field, suffix = f
                        row_data.append({
                            "$field": field,
                            "field": field.field.id,
                            "record": field.record.id,
                            "suffix": suffix,
                            "value": row[ix],
                            "filename": filename.name,
                            "sheet": dataset.title,
                            "row": row_ix,
                            "file_sha512": digest,
                        })

                unique_id = _pick_value(row_data, field="unique_id")
                if not unique_id:
                    print("Unique ID not found in", row_data)

                for c in row_data:
                    field = c['$field']
                    keys = [f for f in field.record.primary_keys]
                    key_values = []
                    for key in keys:
                        if key.foreign_keys:
                            for fk in key.foreign_keys:
                                key_values.append(_pick_value(row_data, field=fk['field'], record=fk['record']))
                        else:
                            key_val = _pick_value(row_data, field=key.id, suffix=c['suffix'])
                            key_values.append(key_val)
                            if key_val == "":
                                c['empty_key'] = True
                    c['primary_key'] = key_values
                    del c['$field']

                parsed_data += [r for r in row_data if not r.get('empty_key')]

        return parsed_data
