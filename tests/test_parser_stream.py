import random
import unittest
from pathlib import Path

import tablib

from rtofdata.parser import pick_value, fix_field_id, file_to_databook, Parser
from rtofdata.specification.parser import parse_specification


class TestParserUtil(unittest.TestCase):

    def test_basic_to_eventstream(self):
        spec = parse_specification()
        parser = Parser(spec)

        db = tablib.Dataset(
            ['1', '1998'],
            headers=['unique_id', 'year_of_birth']
        )
        events = parser.databook_to_events(tablib.Databook([db]))
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertDictEqual(event, {
            "field": "year_of_birth",
            "record": "person",
            "row": 0,
            "sheet": None,
            "suffix": "",
            "value": "1998",
            "primary_key": {
                "unique_id": "1",
            },
        })

    def test_many_to_one_eventstream(self):
        spec = parse_specification()
        parser = Parser(spec)

        db = tablib.Dataset(
            ['1', 'Test Key', 'Test Value'],
            headers=['unique_id', 'integration_outcome_type', 'integration_social']
        )
        events = parser.databook_to_events(tablib.Databook([db]))
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertDictEqual(event, {
            "field": "integration_social",
            "record": "integration_plan",
            "row": 0,
            "sheet": None,
            "suffix": "",
            "value": "Test Value",
            "primary_key": {
                "unique_id": "1",
                "integration_outcome_type": "Test Key",
            },
        })