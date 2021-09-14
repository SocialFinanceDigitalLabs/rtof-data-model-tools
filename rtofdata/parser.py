#!/usr/bin/env python
import hashlib
import re

import tablib
import yaml

from rtofdata.specification.parser import parse_specification

from rtofdata.config import output_dir
spec = parse_specification()
field_ids = [f for f in spec.fields if not f.field.foreign_keys]

ptn_field_id = re.compile(r"[^a-z0-9]")


def fix_field_id(field_id):
    if field_id is None:
        return None
    return ptn_field_id.sub("", field_id.lower())


def get_by_field_id(field_id):
    field_id = fix_field_id(field_id)
    for f in field_ids:
        fid = fix_field_id(f.field.id)
        if field_id.startswith(fid):
            return f, field_id[len(fid):]


sample_dir = output_dir / 'samples'
input_files = list(sample_dir.glob("*.csv")) + list(sample_dir.glob("*.xlsx"))


def _pick_value(row_data, **kwargs):
    def _matches(c):
        for key, value in kwargs.items():
            if c.get(key) != value:
                return False
        return True

    matches = [c['value'] for c in row_data if _matches(c)]
    if matches:
        return matches[0]


parsed_data = []

for filename in input_files:
    if filename.suffix == ".csv":
        with open(filename, 'rt') as fh:
            dataset = tablib.Dataset().load(fh, format="csv")
            databook = tablib.Databook([dataset])
    elif filename.suffix == ".xlsx":
        with open(filename, 'rb') as fh:
            databook = tablib.Databook().load(fh, format="xlsx")
    else:
        print("Unknown file type", filename)
        continue

    with open(filename, 'rb') as fh:
        digest = hashlib.sha512(fh.read())
    digest = digest.hexdigest()

    for dataset in databook.sheets():
        fields = [get_by_field_id(h) for h in dataset.headers]
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
                        key_values.append(_pick_value(row_data, field=key.id, suffix=c['suffix']))
                c['primary_key'] = key_values
                del c['$field']

            parsed_data += row_data

print("Parse complete")
with open(output_dir / "parsed_output.yaml", "wt") as file:
    yaml.dump(parsed_data, file, sort_keys=False)

print("Output saved")
