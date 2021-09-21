import unittest

from rtofdata.datasource.in_memory import InMemoryDataSource
from rtofdata.parser.parser import DataEvent
from rtofdata.specification.parser import parse_specification


class TestParserUtil(unittest.TestCase):
    spec = parse_specification()

    def _gen_event(self, record_id, field_id, value, **primary_keys):
        pk = self.spec.record_by_id(record_id).get_key(**primary_keys)
        return DataEvent(
            record=record_id,
            field=field_id,
            value=value,
            primary_key=pk
        )

    def test_basic_to_eventstream(self):
        events = [
            self._gen_event("person", "year_of_birth", "1989", unique_id="DP-14"),
            self._gen_event("person", "gender", "Woman", unique_id="DP-14"),
        ]

        ds = InMemoryDataSource()
        for e in events:
            ds.update(e)

        self.assertDictEqual(
            dict(unique_id="DP-14", year_of_birth="1989", gender="Woman"),
            ds.get_single_record("person", "DP-14")
        )

        ds.update(self._gen_event("person", "gender", "Man", unique_id="DP-14"))

        self.assertDictEqual(
            dict(unique_id="DP-14", year_of_birth="1989", gender="Man"),
            ds.get_single_record("person", "DP-14")
        )
