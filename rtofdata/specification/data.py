from collections import namedtuple
from dataclasses import dataclass
from typing import List, Any

import humps

FieldRecord = namedtuple("FieldRecord", ["field", "record", "flow"])


@dataclass
class Datatype:
    id: str
    description: str = None
    extends: str = None

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
    validation: List = None
    dimensions: DimensionList = None
    status: str = None
    latest_comments: dict = None

    def validation_get(self, key, default_value=None):
        for v in self.validation:
            if v['id'] == key:
                return v['args']
        return default_value


@dataclass
class Record:
    id: str
    description: str = None
    fields: List[Field] = None

    @property
    def primary_keys(self) -> List[Field]:
        return [f for f in self.fields or [] if f.primary_key]

    @property
    def foreign_keys(self) -> List[Field]:
        return [f for f in self.fields or [] if f.foreign_keys]

    @property
    def key_class(self) -> namedtuple:
        return namedtuple(humps.pascalize(f"{self.id}_key"), ['record'] + [k.id for k in self.primary_keys])

    @property
    def record_class(self) -> namedtuple:
        return namedtuple(humps.pascalize(f"{self.id}_record"), [f.id for f in self.fields])

    def get_key(self, **kwargs):
        return self.key_class(record=self.id, **kwargs)

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
    datatypes: List[Datatype]

    @property
    def fields(self):
        for flowrecord in self.records_by_flow:
            for field in flowrecord.record.fields:
                yield FieldRecord(field, flowrecord.record, flowrecord.flow)

    def record_by_id(self, id):
        return [r for r in self.records if r.id == id][0]

    def record_references(self, record_name):
        references = []
        for other_rec in self.records:
            for fk_field in other_rec.foreign_keys:
                for fk in fk_field.foreign_keys:
                    if fk['record'] == record_name:
                        references.append(dict(record=other_rec, field=fk_field, foreign_key=fk))
        return references

    @property
    def top_level_records(self):
        for rec in self.records:
            fks = [f for f in rec.fields if f.foreign_keys]
            if len(fks) == 0:
                yield rec

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
