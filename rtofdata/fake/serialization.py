import re

import tablib

from rtofdata.specification.data import Specification


def dataset_to_tablib(dataset, spec: Specification):
    dataset_list = []
    for record_name, items in dataset.items():
        record = spec.record_by_id(record_name)
        items = [i for i in items.values()]
        data = tablib.Dataset()
        dataset_list.append(data)
        data.headers = [f.id for f in record.fields]
        data.title = record_name
        for item in items:
            data.append([item.get(h) for h in data.headers])
    return dataset_list


def dataset_to_wide(dataset, spec: Specification):
    columns = []
    for record in spec.records_by_flow:
        record = record.record
        pks = [f for f in record.fields if f.primary_key]
        unique_values = None

        valid_fields = []
        for f in record.fields:
            if f.primary_key and f.foreign_keys:
                continue
            if f.primary_key and len(pks) > 1:
                unique_values = {v[f.id] for v in dataset[record.id].values()}
            valid_fields.append(f)

        if unique_values:
            for v in unique_values:
                header = re.sub(r'[^a-z0-9]', '', v.lower())
                for f in valid_fields:
                    columns.append(dict(field=f.id, value=v, header=f"{f.id}_{header}"))
        else:
            for f in valid_fields:
                columns.append(dict(header=f.id))

    data = tablib.Dataset()
    data.headers = [f['header'] for f in columns]

    for record_name, items in dataset.items():
        items = [i for i in items.values()]
        for item in items:
            data.append([item.get(h) for h in data.headers])
