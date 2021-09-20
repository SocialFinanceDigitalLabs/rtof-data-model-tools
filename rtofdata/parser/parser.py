from pathlib import Path
from typing import List

from rtofdata.parser import fix_field_id, file_to_databook, file_to_digest, pick_value
from rtofdata.specification.data import Specification


class Parser:
    def __init__(self, spec: Specification):
        self.__spec = spec
        self.__all_fields = [(fix_field_id(f.field.id), f) for f in spec.fields if not f.field.foreign_keys]

    def parse_file(self, filename: Path) -> List:
        databook = file_to_databook(filename)
        digest = file_to_digest(filename)
        return self.databook_to_events(databook, filename=filename.name, digest=digest)

    def get_by_field_id(self, field_id):
        field_id = fix_field_id(field_id)
        for fid, field in self.__all_fields:
            if field_id.startswith(fid):
                return field, field_id[len(fid):]

    def databook_to_events(self, databook, filename=None, digest=None):
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
                        entry = {
                            "$field": field,
                            "field": field.field.id,
                            "record": field.record.id,
                            "suffix": suffix,
                            "value": row[ix],
                            "sheet": dataset.title,
                            "row": row_ix,
                        }
                        if filename:
                            entry["filename"] = filename
                        if digest:
                            entry['file_sha512'] = digest
                        row_data.append(entry)

                for c in row_data:
                    field = c['$field']
                    keys = [f for f in field.record.primary_keys]
                    key_values = {}
                    for key in keys:
                        if key.foreign_keys:
                            for fk in key.foreign_keys:
                                key_values[key.id] = pick_value(row_data, field=fk['field'], record=fk['record'])
                        else:
                            key_val = pick_value(row_data, field=key.id, suffix=c['suffix'])
                            key_values[key.id] = key_val
                    c['primary_key'] = key_values

                by_key = {}
                for d in row_data:
                    if not d['$field'].field.primary_key:
                        del d['$field']
                        by_key.setdefault((d['record'], *d['primary_key']), []).append(d)

                for key, record_data in by_key.items():
                    values = [r['value'] for r in record_data if r['value'] != ""]
                    if len(values) > 0:
                        parsed_data += record_data

        return parsed_data