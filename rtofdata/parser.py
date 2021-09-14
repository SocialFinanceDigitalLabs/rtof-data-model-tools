#!/usr/bin/env python

from dataclasses import field, fields
import os
from os import name
from re import X, match
from typing import ChainMap
from typing_extensions import Concatenate
from rtofdata.specification.data import Record
import tablib
from collections import namedtuple
FieldRecord = namedtuple("FieldRecord", ["field", "record", "flow"])
from rtofdata.specification.parser import parse_specification, validate_specification
from collections import defaultdict
from functools import reduce
from itertools import chain, groupby

from rtofdata.config import output_dir
spec = parse_specification()
field_ids = [f.field.id for f in spec.fields if not f.field.foreign_keys]


data = [output_dir / 'samples/sample_record_person.csv', output_dir / 'samples/sample_record_baseline.csv']

folderpath = output_dir / 'samples'

filepaths = [os.path.join(folderpath, name) for name in os.listdir(folderpath)] 

all_files = []
for path in data:
    with open(path, 'r') as fh:
        file = tablib.Dataset().load(fh)
        all_files.append(file)

all_data = []
for file in all_files:    
    data_i = file.dict
    all_data += data_i

combine_on_id = map(lambda dict_tuple: dict(ChainMap(*dict_tuple[1])), 
    groupby(sorted(all_data, key = lambda sub_dict: sub_dict["unique_id"]), 
    key= lambda sub_dict: sub_dict["unique_id"]))

unique_id_combine = list(combine_on_id)
print(unique_id_combine[:2])



#for file in all_files:
 # fields_included = [x for x in field_ids if x in file.headers]
#for file in all_files:
 # fields_not_included = [x for x in field_ids if x not in  file.headers]

#(f"Fields included in this submission: {fields_included}")
#(f"Fields not included in this submission: {fields_not_included}")