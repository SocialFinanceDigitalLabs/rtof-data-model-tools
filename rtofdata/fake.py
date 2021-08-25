import argparse
from datetime import timedelta

import yaml
from faker import Faker

from rtofdata.config import output_dir, template_dir
from rtofdata.spec_parser import parse_specification
from rtofdata import fake_generator


def generate_records(datastore, spec, context, record_name, config):
    local_context = config.get('context', {})
    if isinstance(local_context.get("start"), int):
        local_context['start'] = context['date'] + timedelta(days=local_context['start'])
    if isinstance(local_context.get("end"), int):
        local_context['end'] = context['date'] + timedelta(days=local_context['end'])

    context = {**context, **local_context}

    faker = Faker()
    if "seed" in context:
        faker.seed_instance(context["seed"])

    for ix in range(0, config.get("num", 1)):
        if faker.random.random() > config['probability']:
            continue
        record_context = {**context, "date": faker.date_between(context['start'], context['end'])}

        id, record = generate_record(spec, record_context, record_name, config, faker, ix)
        datastore.setdefault(record_name, {})[id] = record

        record_context["parent_id"] = id
        record_context["seed"] = faker.random.randint(0, 1000000)

        for sub_record_name, sub_config in config.get('records', {}).items():
            generate_records(datastore, spec, record_context, sub_record_name, sub_config)


def generate_record(spec, context, record_name, config, faker, ix):
    record_spec = spec.record_by_id(record_name)
    record = {}

    id = []
    for f in record_spec.fields:
        if f.foreign_keys:
            gen = lambda *args, **kwargs: context['parent_id']
            args = {}
        elif f.sample_generator:
            gen = getattr(fake_generator, f.sample_generator['method'])
            args = f.sample_generator.get('args', {})
        else:
            gen = getattr(fake_generator, f.type.id)
            args = {}

        record[f.id] = gen(faker, context, field=f, **args)
        if f.primary_key:
            id.append(record[f.id])

    return id[0] if len(id) < 2 else tuple(id), record


def create_all_data(config_file):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Create fake data'
    )
    parser.add_argument("config_file", type=str, nargs='?', help="The sample input generator")
    args = parser.parse_args()
    generated = create_all_data(args.config_file)
    with open(output_dir / "sample.yml", "wt") as file:
        yaml.dump(generated, file, sort_keys=False)



