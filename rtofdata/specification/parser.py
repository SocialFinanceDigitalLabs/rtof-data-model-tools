from typing import List

from dacite import from_dict
import traceback
import yaml
from rtofdata.config import data_dir
from rtofdata.specification import data as rtofdata


def parse_dimensions():
    category_file_list = (data_dir / "categories").glob("*.yml")

    all_categories = []
    for category_file in category_file_list:
        category_id = category_file.stem
        category_list = []
        all_categories.append(rtofdata.DimensionList(id=category_id, dimensions=category_list))
        with open(category_file, 'rt') as file:
            data = yaml.safe_load(file)
        for datum in data:
            if "value" in datum:
                category_list.append(rtofdata.Dimension(**datum))
            else:
                category_list.append(rtofdata.Dimension(value=datum))

    return all_categories


def _get_validator_description(name, config):
    if name == 'conditional':
        return f"conditional rules apply"
    elif isinstance(config, list):
        return f"{name}({', '.join(config)})"
    elif isinstance(config, dict):
        return f"{name}({', '.join([f'{k}={v}' for k, v in config.items()])})"
    else:
        return f"{name}({config})"


def parse_records(datatypes, categories, validators):
    categories = {c.id: c for c in categories}
    datatypes = {c.id: c for c in datatypes}
    validators = {c.id: c for c in validators}

    record_file_list = (data_dir / "records").glob("*.yml")

    record_list = []
    record_errors = []
    for record_file in record_file_list:
        with open(record_file, 'rt') as file:
            record_id = record_file.stem
            data = yaml.safe_load(file)

        field_dict = data.get('fields', {})
        data['fields'] = field_list = []
        for field_id, values in field_dict.items():
            try:
                values['type'] = datatypes[values['type']]
                field = rtofdata.Field(id=field_id, **values)
                if "validation" in values:
                    field.validation = [
                        {
                            "id": k,
                            "args": v,
                            "rule": validators[k],
                            "description": _get_validator_description(k, v)
                        }
                        for k, v in values['validation'].items()
                    ]
                else:
                    field.validation = []
                if "dimension" in values.get('validation', {}):
                    field.dimensions = categories[values['validation']['dimension']]
                field_list.append(field)

            except (TypeError, KeyError):
                record_errors.append(dict(
                    msg="Exception occurred when creating field from",
                    record=record_id,
                    field=field_id,
                    values=values,
                    exception=traceback.format_exc(),
                ))

        record_list.append(rtofdata.Record(id=record_id, **data))

    if len(record_errors) > 0:
        print("Input validation errors encountered:")
        for r in record_errors:
            print(f"*** {r['record']}.{r['field']} ***")
            print(f"{r['exception']}")
            print()

        error_fields = [f"{r['record']}.{r['field']}" for r in record_errors]
        raise ValueError(f"Error in the following fields: {error_fields}")

    return record_list


def parse_flow(records: List[rtofdata.Record]):
    records = {r.id: r for r in records}
    with open(data_dir / "workflow.yml", 'rt') as file:
        data = yaml.safe_load(file)

    flows = []
    for flow in data:
        flow = from_dict(data_class=rtofdata.Workflow, data=flow)
        for step in flow.all_steps:
            step["step"].records = [records[r.id] for r in step['step'].records or []]
        flows.append(flow)

    return flows


def parse_validators():
    with open(data_dir / "validators.yml", 'rt') as file:
        data = yaml.safe_load(file)

    validators = []
    for key, value in data.items():
        validators.append(rtofdata.ValidationRule(id=key, **value))
    return validators


def parse_datatypes():
    with open(data_dir / "datatypes.yml", 'rt') as file:
        data = yaml.safe_load(file)

    datatypes = []
    for key, value in data.items():
        datatypes.append(rtofdata.Datatype(id=key, **value))
    return datatypes


def validate_specification(spec: rtofdata.Specification):
    """
    Look for inconsistencies in the specification
    :return:
    """
    fields = set()
    for field_record in spec.fields:
        if not field_record.field.foreign_keys:
            if field_record.field.id in fields:
                raise ValueError(f"Duplicate field definition: {field_record.field.id}")
        fields.add(field_record.field.id)


def parse_specification():
    datatypes = parse_datatypes()
    categories = parse_dimensions()
    validators = parse_validators()

    records = parse_records(datatypes, categories, validators)
    flows = parse_flow(records)

    return rtofdata.Specification(records=records, dimensions=categories, flows=flows, validators=validators,
                         datatypes=datatypes)
