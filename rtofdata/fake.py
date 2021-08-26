import argparse
from datetime import timedelta

import tablib
import yaml
from faker import Faker

from rtofdata.config import output_dir, template_dir
from rtofdata.fake_generator import get_date_or_delta
from rtofdata.spec_parser import parse_specification
from rtofdata import fake_generator


def generate_records(datastore, spec, context, record_name, config):
    local_context = config.get('context', {})
    if "start" in local_context:
        local_context['start'] = get_date_or_delta(local_context.get("start"), context['date'])
    if "end" in local_context:
        local_context['end'] = get_date_or_delta(local_context.get("end"), context['date'])

    context = {**context, **local_context}

    faker = Faker()
    if "seed" in context:
        faker.seed_instance(context["seed"])

    for ix in range(0, config.get("num", 1)):
        if faker.random.random() > config.get('probability', 1.0):
            continue
        record_context = {**context, "date": faker.date_between(context['start'], context['end'])}

        id, record = generate_record(spec, record_context, record_name, config, faker, ix)
        datastore.setdefault(record_name, {})[id] = record

        if "parent_id" not in record_context:
            record_context["parent_id"] = id
        record_context["seed"] = faker.random.randint(0, 1000000)

        for sub_record_name, sub_config in config.get('records', {}).items():
            generate_records(datastore, spec, record_context, sub_record_name, sub_config)


def generate_record(spec, context, record_name, config, faker, ix):
    record_spec = spec.record_by_id(record_name)
    record = {}

    id = []
    for f in record_spec.fields:
        field_config = config.get("fields", {}).get(f.id, {})
        if f.foreign_keys:
            gen = lambda *args, **kwargs: context['parent_id']
            args = {}
        elif "method" in field_config:
            gen = getattr(fake_generator, field_config['method'])
            args = field_config.get('args', {})
        else:
            gen = getattr(fake_generator, f.type.id)
            args = {}

        record[f.id] = gen(faker, context, field=f, **args)
        if f.primary_key:
            id.append(record[f.id])

    return id[0] if len(id) < 2 else tuple(id), record


def create_all_data(config_file=None):
    spec = parse_specification()

    if config_file is None:
        config_file = template_dir / "samples/small.yml"

    with open(config_file, "rt") as file:
        gen_spec = yaml.safe_load(file)

    context = gen_spec.get('context', {})
    records = gen_spec.get('records', {})

    datastore = {}
    for record_name, config in records.items():
        generate_records(datastore, spec, context, record_name, config)

    return datastore


def dataset_to_tablib(dataset):
    dataset_list = []
    for record_name, items in dataset.items():
        items = [i for i in items.values()]
        data = tablib.Dataset()
        dataset_list.append(data)
        data.headers = [k for k in items[0].keys()]
        data.title = record_name
        for item in items:
            data.append(item.values())
    return dataset_list


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create fake data'
    )
    parser.add_argument("config_file", type=str, nargs='?', help="The sample input generator")
    args = parser.parse_args()
    generated = create_all_data(args.config_file)

    dataset = dataset_to_tablib(generated)
    book = tablib.Databook(dataset)

    with open(output_dir / "sample.xlsx", "wb") as file:
        file.write(book.export('xlsx'))

    with open(output_dir / "sample.yml", "wt") as file:
        file.write(book.export('yaml'))


