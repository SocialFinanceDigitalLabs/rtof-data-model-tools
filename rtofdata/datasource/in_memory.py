from rtofdata.parser.parser import DataEvent


class InMemoryDataSource:

    def __init__(self):
        self.datastore = {}

    def update(self, event: DataEvent):
        key_values = event.primary_key._asdict()
        del key_values['record']
        self.datastore.setdefault(
            event.record, {}
        ).setdefault(
            tuple(event.primary_key[1:]), {**key_values}
        )[event.field] = event.value

    def get_records_by_type(self, record):
        return self.datastore.get(record)

    def get_single_record(self, record, *keys):
        records = self.get_records_by_type(record)
        if not records:
            return None

        return records.get(tuple(keys))
