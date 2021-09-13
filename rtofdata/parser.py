#!/usr/bin/env python

from dataclasses import field, fields
from os import name
from re import X
from rtofdata.specification.data import Record
import tablib
from collections import namedtuple
FieldRecord = namedtuple("FieldRecord", ["field", "record", "flow"])
from rtofdata.specification.parser import parse_specification, validate_specification

from rtofdata.config import output_dir
spec = parse_specification()

data = output_dir / 'samples/sample_record_person.csv'


with open(data, 'r') as fh:
    data_tab = tablib.Dataset().load(fh)

headers = data_tab.headers

field_ids = [f.field.id for f in spec.fields if not f.field.foreign_keys]


fields_included = [x for x in field_ids if x in headers]
fields_not_included = [x for x in field_ids if x not in  headers]

x = data_tab.dict
(x[:10])

print(x[:1])
print(f"Fields not included in this submission {fields_not_included}")
