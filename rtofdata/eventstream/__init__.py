from rtofdata.specification.data import Specification


class StreamParser:

    def __init__(self, spec: Specification):
        self.__records = {}
        self.__spec = spec

    def parse_stream(self, stream_input):
        for event in stream_input:
            self.process_event(event)

    def process_event(self, event):
        key = (event['record'], *event['primary_key'])
        record = self.__spec.record_by_id(event['record'])
        record_data = self.__records.setdefault(key, {})

        for ix, pk in enumerate(record.primary_keys):
            record_data[pk.id] = key[ix+1]
        record_data[event['field']] = event['value']

    @property
    def records(self):
        for r in self.__records.values():
            yield r
