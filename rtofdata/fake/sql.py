import humps
import re
import sqlalchemy
import sqlalchemy.orm
import tablib
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from rtofdata.specification.data import Specification


def create_schema(spec: Specification):
    metadata_obj = sqlalchemy.MetaData()

    for record in spec.records_by_flow:
        record = record.record
        columns = []
        for f in record.fields:
            column_type = f.type.extends if f.type.extends else f.type.id
            if column_type == "string":
                length = f.validation_get("character_limit", 255)
                if length <= 255:
                    column_type = sqlalchemy.String(length)
                else:
                    column_type = sqlalchemy.Text
            elif column_type == "integer":
                column_type = sqlalchemy.Integer
            elif column_type == "date":
                column_type = sqlalchemy.Date
            else:
                raise ValueError(f"Unknown field type: {column_type}")

            args = [f.id, column_type]
            kwargs = {}

            if f.primary_key:
                kwargs['primary_key'] = True
            if f.foreign_keys:
                for key in f.foreign_keys:
                    args.append(sqlalchemy.ForeignKey(f"{key['record']}.{key['field']}"))
            if f.validation_get("required", False):
                kwargs['nullable'] = False

            columns.append(sqlalchemy.Column(*args, **kwargs))

        sqlalchemy.Table(record.id, metadata_obj, *columns)

    return metadata_obj


def insert_into_database(engine, metadata_obj, dataset):
    for record_name, items in dataset.items():
        items = [i for i in items.values()]
        table = sqlalchemy.Table(record_name, metadata_obj, autoload_with=engine)
        with engine.connect() as conn:
            for item in items:
                stmt = sqlalchemy.insert(table).values(**item)
                conn.execute(stmt)


def get_orm_mappings(spec, engine):
    """
    We here build our ORM Mapped Tables by autoloading the properties and adding
    references.

    We declared ORM classes using "pascalized" versions of the record name,
    e.g. housing_entry => HousingEntry

    Each ORM class have relationship properties for both One-To-Many and Many-To-One relationships.

    :param spec:
    :param engine:
    :return:
    """
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    meta = Base.metadata

    def my_str(self):
        values = []
        for field in self._record_.fields:
            values.append(f"{field.id}={getattr(self, field.id)}")
        return f"{humps.pascalize(self._record_.id)}({', '.join(values)})"

    table_mappings = {}
    for r in spec.records:
        table_name = r.id
        properties = {
            "__table__": sqlalchemy.Table(table_name, meta, autoload_with=engine),
            "__str__": my_str,
            "_record_": r,
        }
        # Declare ManyToOne relationships, e.g. baseline -> person
        for field in r.foreign_keys:
            for fk in field.foreign_keys:
                record_id = fk['record']
                properties[record_id] = sqlalchemy.orm.relationship(humps.pascalize(record_id),
                                                                    back_populates=table_name)

        # Declare OneToMany relationships, e.g. person -> integration_plan
        for ref in spec.record_references(table_name):
            record_id = ref['record'].id
            other_record = spec.record_by_id(record_id)
            # This is not generic - but if only one PK we guess OneToOne
            one_to_one = len(other_record.primary_keys) == 1
            properties[record_id] = sqlalchemy.orm.relationship(humps.pascalize(record_id), uselist=not one_to_one)

        table_mappings[table_name] = type(humps.pascalize(table_name), (Base,), properties)

    return table_mappings


def database_to_wide(engine, spec: Specification):
    Session = sessionmaker(bind=engine)
    session = Session()

    table_mapping = get_orm_mappings(spec, engine)

    entries = dict()
    headers = dict()
    for record in spec.records_by_flow:
        record = record.record

        # WARNING: Not generic
        entity = table_mapping[record.id]
        for row in session.execute(select(entity)):
            row = row[0]
            entry = entries.setdefault(row.unique_id, {})
            if record.id == "integration_plan":
                io_type = row.integration_outcome_type
                suffix = "_" + re.sub(r'[^a-z0-9]', '', io_type.lower())
            else:
                suffix = ""

            for f in record.fields:
                if not f.foreign_keys:
                    header = f"{f.id}{suffix}"
                    entry[header] = getattr(row, f.id)
                    headers[header] = None

    data = tablib.Dataset()
    data.headers = headers = [k for k in headers.keys()]
    for entry in entries.values():
        data.append([entry.get(k) for k in headers])

    return data
