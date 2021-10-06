from rtofdata.datasource import DataSource
from rtofdata.parser.parser import DataEvent
from rtofdata.specification.data import Specification


class InMemoryDataSource(DataSource):

    def __init__(self, spec: Specification):
        self.datastore = {}
        self.__spec = spec
        self.__record_tuples = rt = {}
        for record in spec.records:
            rt[record.id] = record.record_class

    def update(self, event: DataEvent):
        key = tuple(event.primary_key[1:])

        record_id = event.record

        record = self.get_single_record(record_id, *key)

        record_class = self.__record_tuples[record_id]
        record_values = {f: None for f in record_class._fields}
        if record:
            record_values.update(record._asdict())
        else:
            record_values.update(event.primary_key._asdict())
            del record_values['record']

        record_values[event.field] = event.value

        self.datastore.setdefault(record_id, {})[key] = value = record_class(**record_values)
        return value

    def get_records_by_type(self, record: str):
        return self.datastore.get(record)

    def get_single_record(self, record: str, *keys):
        records = self.get_records_by_type(record)
        if not records:
            return None

        return records.get(keys)
