import re

import yaml
from faker import Faker
from tqdm import trange

from rtofdata.config import template_dir
from rtofdata.fake import generators
from rtofdata.fake.generators import get_date_or_delta
from rtofdata.specification.parser import parse_specification

faker = Faker()

ptn_conditional = re.compile(r'(\w+)\((.*)\)')


def generate_records(datastore, spec, context, record_name, config, progress=False):
    local_context = config.get('context', {})
    if "start" in local_context:
        local_context['start'] = get_date_or_delta(local_context.get("start"), context['date'])
    if "end" in local_context:
        local_context['end'] = get_date_or_delta(local_context.get("end"), context['date'])

    context = {**context, **local_context}

    if "seed" in context:
        Faker.seed(context["seed"])
        del context["seed"]

    my_range = trange if progress else range

    for ix in my_range(0, config.get("num", 1)):
        if faker.random.random() > config.get('probability', 1.0):
            continue
        record_context = {**context, "date": faker.date_between(context['start'], context['end'])}

        id, record = generate_record(spec, record_context, record_name, config, faker, ix)
        datastore.setdefault(record_name, {})[id] = record

        if "parent_id" not in record_context:
            record_context["parent_id"] = id

        for sub_record_name, sub_config in config.get('records', {}).items():
            generate_records(datastore, spec, record_context, sub_record_name, sub_config)


def generate_field_value(faker, context, field, field_config, record):
    validators = [v['description'] for v in field.validation]
    probability = 1.0 if "required(True)" in validators else 0.5
    probability = field_config.get("probability", probability)

    if faker.random.random() > probability:
        return None

    if field.foreign_keys:
        gen = lambda *args, **kwargs: context['parent_id']
    elif "method" in field_config:
        gen = getattr(generators, field_config['method'])
    else:
        gen = getattr(generators, field.type.id)

    args = {}
    if "args" in field_config:
        args = field_config.get('args', {})

    return gen(faker, context, field=field, record=record, **args)


def generate_record(spec, context, record_name, config, faker, ix):
    record_spec = spec.record_by_id(record_name)
    record = {}

    fields_to_generate = {f.id: f for f in record_spec.fields}

    id = []
    next_field = None
    while len(fields_to_generate) > 0:
        if next_field:
            field_id = next_field
            next_field = None
        else:
            field_id = next(iter(fields_to_generate))
        field = fields_to_generate[field_id]
        field_config = config.get("fields", {}).get(field.id, {})
        field_config = {k: v for k, v in field_config.items()}

        required_if = field_config.get("required_if")
        if required_if:
            match = ptn_conditional.match(required_if)
            rule_name = match.group(1)
            rule_value = match.group(2)
            if rule_name == "one_of":
                referenced_field = rule_value.split(",", 1)[0].strip()
                if referenced_field not in record:
                    next_field = referenced_field
                    continue
                value = record[referenced_field]
                must_be = rule_value.split(",", 1)[1].strip()
                must_be = yaml.safe_load(must_be)
                if isinstance(must_be, list):
                    if value in must_be:
                        field_config['probability'] = 1
                else:
                    if value == must_be:
                        field_config['probability'] = 1
            else:
                raise ValueError(f"Unknown rule: {rule_name}")

        record[field_id] = generate_field_value(faker, context, field, field_config, record)
        if field.primary_key:
            id.append(record[field_id])

        del fields_to_generate[field_id]

    return id[0] if len(id) < 2 else tuple(id), record


def create_all_data(spec=None, config_file=None, num=None, progress=False):
    if not spec:
        spec = parse_specification()

    if config_file is None:
        config_file = template_dir / "samples/small.yml"

    with open(config_file, "rt") as file:
        gen_spec = yaml.safe_load(file)

    context = gen_spec.get('context', {})
    records = gen_spec.get('records', {})

    datastore = {}
    for record_name, config in records.items():
        if num:
            config["num"] = num
        generate_records(datastore, spec, context, record_name, config, progress=progress)

    return datastore