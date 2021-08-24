from dataclasses import dataclass
from typing import List, Any
from dacite import from_dict
import traceback

import yaml

from rtofdata.config import data_dir


@dataclass
class Datatype:
    id: str
    description: str = None

    def __str__(self):
        return self.id


@dataclass
class Dimension:
    value: str
    description: str = None


@dataclass
class DimensionList:
    id: str
    dimensions: List[Dimension]

    @property
    def values(self):
        return [d.value for d in self.dimensions]


@dataclass
class Field:
    id: str
    name: str
    type: Datatype
    description: str = None
    comments: str = None
    primary_key: bool = False
    foreign_keys: List = None
    validation: dict = None
    dimensions: DimensionList = None
    sample_generator: dict = None
    status: str = None
    latest_comments: dict = None


@dataclass
class Record:
    id: str
    description: str = None
    fields: List[Field] = None

    @property
    def primary_keys(self) -> List[Field]:
        return [f for f in self.fields or [] if f.primary_key]

    def field_by_id(self, id):
        return [r for r in self.fields if r.id == id][0]


@dataclass
class Workflow:
    name: str
    color: str
    steps: List["WorkflowStep"]

    @property
    def all_steps(self):
        all_steps = []
        for s in self.steps:
            all_steps += s.all_steps
        for s in all_steps:
            if "flow" not in s:
                s["flow"] = self
        return all_steps


@dataclass
class WorkflowStep:
    name: str
    records: List[Record] = None
    flows: List[Workflow] = None

    @property
    def all_steps(self) -> List[Any]:
        all_steps = [dict(step=self)]
        for f in self.flows or []:
            all_steps += f.all_steps
        return all_steps


@dataclass
class RecordInFlow:
    flow: Workflow
    record: Record


@dataclass
class ValidationRule:
    id: str
    description: str
    args: List


@dataclass
class Specification:
    records: List[Record]
    dimensions: List[DimensionList]
    flows: List[Workflow]
    validators: List[ValidationRule]

    def record_by_id(self, id):
        return [r for r in self.records if r.id == id][0]

    def dimension_by_id(self, id):
        return [r for r in self.dimensions if r.id == id][0]

    def field_by_id(self, record_id, field_id):
        record = self.record_by_id(record_id)
        return record.field_by_id(field_id)

    def validator_by_id(self, id):
        return [r for r in self.validators if r.id == id][0]

    @property
    def records_by_flow(self):
        flow_steps = []
        for flow in self.flows or []:
            flow_steps += flow.all_steps

        all_keys = set()
        flow_records = []
        for step in flow_steps:
            for record in step["step"].records or []:
                if record.id not in all_keys:
                    all_keys.add(record.id)
                    flow_records.append(RecordInFlow(flow=step["flow"], record=record))

        return flow_records


def parse_dimensions():
    category_file_list = (data_dir / "categories").glob("*.yml")

    all_categories = []
    for category_file in category_file_list:
        category_id = category_file.stem
        category_list = []
        all_categories.append(DimensionList(id=category_id, dimensions=category_list))
        with open(category_file, 'rt') as file:
            data = yaml.safe_load(file)
        for datum in data:
            if "value" in datum:
                category_list.append(Dimension(**datum))
            else:
                category_list.append(Dimension(value=datum))

    return all_categories


def parse_records(datatypes, categories):
    categories = {c.id: c for c in categories}
    datatypes = {c.id: c for c in datatypes}

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
                field = Field(id=field_id, **values)
                field_list.append(field)
                if "dimension" in field.validation:
                    field.dimensions = categories[field.validation['dimension']]

            except (TypeError, KeyError):
                record_errors.append(dict(
                    msg="Exception occurred when creating field from",
                    record=record_id,
                    field=field_id,
                    values=values,
                    exception=traceback.format_exc(),
                ))

        record_list.append(Record(id=record_id, **data))

    if len(record_errors) > 0:
        print("Input validation errors encountered:")
        for r in record_errors:
            print(f"*** {r['record']}.{r['field']} ***")
            print(f"{r['exception']}")
            print()

        error_fields = [f"{r['record']}.{r['field']}" for r in record_errors]
        raise ValueError(f"Error in the following fields: {error_fields}")

    return record_list


def parse_flow(records: List[Record]):
    records = {r.id: r for r in records}
    with open(data_dir / "workflow.yml", 'rt') as file:
        data = yaml.safe_load(file)

    flows = []
    for flow in data:
        flow = from_dict(data_class=Workflow, data=flow)
        for step in flow.all_steps:
            step["step"].records = [records[r.id] for r in step['step'].records or []]
        flows.append(flow)

    return flows


def parse_validators():
    with open(data_dir / "validators.yml", 'rt') as file:
        data = yaml.safe_load(file)

    validators = []
    for key, value in data.items():
        validators.append(ValidationRule(id=key, **value))
    return validators


def parse_datatypes():
    with open(data_dir / "datatypes.yml", 'rt') as file:
        data = yaml.safe_load(file)

    datatypes = []
    for key, value in data.items():
        datatypes.append(Datatype(id=key, **value))
    return datatypes


def parse_specification():
    datatypes = parse_datatypes()
    validators = parse_validators()
    categories = parse_dimensions()

    records = parse_records(datatypes, categories)
    flows = parse_flow(records)

    return Specification(records=records, dimensions=categories, flows=flows, validators=validators)
