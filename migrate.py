#!/usr/bin/env python

import argparse
from itertools import zip_longest

import yaml

from rtofdata.util.config import data_dir
from rtofdata.excel import read_excel


def mutate_fields(field_list):
    field_list = [{k.lower(): v for k, v in f.items()} for f in field_list]
    field_dict = {f['id']: {**f} for f in field_list}
    for f in field_dict.values():
        id = f['id']
        del f['id']
        del f['table']

        key_type = f.get("keys")
        if key_type:
            del f["keys"]

        if key_type == "Primary Key":
            f['primary_key'] = True

        if key_type == "Foreign Key":
            f['foreign_keys'] = [dict(record="person", field="ni_number")]

        if "y" in f.get("required", "n").lower():
            f.setdefault('validation', {})['required'] = True

        if "required" in f:
            del f["required"]

        if "after date" in f:
            f.setdefault('validation', {})['date_after'] = f["after date"]
            del f["after date"]

        if "validationrules" in f:
            f.setdefault('validation', {})['extras'] = f["validationrules"]
            del f["validationrules"]

        if f['type'] == "Categorical":
            f.setdefault('validation', {})['dimension'] = id


    return field_dict


def get_definition(value):
    v = value[0]
    d = value[1]
    if d is None:
        return v
    else:
        return dict(value=v, description=d)


class SpacedOutDumper(yaml.SafeDumper):
    # HACK: insert blank lines between top-level objects
    # inspired by https://stackoverflow.com/a/44284819/3786245
    def write_line_break(self, data=None):
        super().write_line_break(data)

        try:
            if self.events[0].value == "fields":
                return
        except:
            pass

        if len(self.indents) <= 2:
            super().write_line_break()


def main(filename):
    data = read_excel(filename, as_list=["Categories"])

    record_list = [dict(id=r['Table'], description=r['Description'].strip()) for r in data['Tables']]
    for record in record_list:
        record['fields'] = mutate_fields([f for f in data['Fields'] if f['Table'] == record['id']])

        with open(data_dir / 'records' / f'{record["id"]}.yml', 'wt') as file:
            file_contents = dict(description=record['description'], fields=record['fields'])
            yaml.dump(file_contents, file, Dumper=SpacedOutDumper, sort_keys=False, allow_unicode=True)

    category_list = data['Categories']
    category_ids = [id for id in category_list.keys() if not id.endswith("_description")]

    for key in category_ids:
        values = category_list[key]
        descriptions = category_list.get(f"{key}_description", [])
        values = zip_longest(values, descriptions)
        values = [get_definition(v) for v in values]

        with open(data_dir / 'categories' / f'{key}.yml', 'wt') as file:
            yaml.dump(values, file, sort_keys=False, allow_unicode=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process the RTOF data specification'
    )
    parser.add_argument('filename', type=str, help='The filename to read')

    args = parser.parse_args()

    main(args.filename)