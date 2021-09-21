import unittest
from dataclasses import asdict

import tablib

from rtofdata.parser import Parser
from rtofdata.specification.parser import parse_specification


class TestParserUtil(unittest.TestCase):

    def test_basic_to_eventstream(self):
        spec = parse_specification()
        parser = Parser(spec)

        dataset = tablib.Dataset(
            ['1', '1998'],
            headers=['unique_id', 'year_of_birth']
        )
        events = parser.dataset_to_events(dataset)
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertDictEqual(asdict(event), {
            "column": 1,
            "field": "year_of_birth",
            "record": "person",
            "row": 0,
            "sheet": None,
            "suffix": "",
            "value": "1998",
            "primary_key": spec.record_by_id(event.record).get_key(unique_id="1"),
            "filename": None,
            "file_sha512": None,
        })

    def test_many_to_one_eventstream(self):
        spec = parse_specification()
        parser = Parser(spec)

        dataset = tablib.Dataset(
            ['1', 'Test Key', 'Test Value'],
            headers=['unique_id', 'integration_outcome_type', 'integration_social']
        )
        events = parser.dataset_to_events(dataset)
        self.assertEqual(len(events), 1)

        event = events[0]
        self.assertEqual(event.value, "Test Value")
        self.assertEqual(
            event.primary_key,
            spec.record_by_id(event.record).get_key(unique_id="1", integration_outcome_type="Test Key")
        )


    def test_multi_eventstream(self):
        spec = parse_specification()
        parser = Parser(spec)

        dataset = tablib.Dataset(
            ['1',
             'Test Key', 'Test Value',
             'Other Key', 'Other Value',
             'Last Key', 'Last Value'
             ],
            headers=['unique_id',
                     'integration_outcome_type_first', 'integration_social_first',
                     'integration_outcome_type_secnd', 'integration_social_secnd',
                     'integration_outcome_type', 'integration_social',
                     ]
        )
        events = parser.dataset_to_events(dataset)
        self.assertEqual(len(events), 3)

        event = events[0]
        self.assertEqual(event.value, "Test Value")
        self.assertEqual(event.suffix, "first")
        self.assertEqual(event.primary_key.integration_outcome_type, "Test Key")

        event = events[1]
        self.assertEqual(event.value, "Other Value")
        self.assertEqual(event.suffix, "secnd")
        self.assertEqual(event.primary_key.integration_outcome_type, "Other Key")

        event = events[2]
        self.assertEqual(event.value, "Last Value")
        self.assertEqual(event.suffix, "")
        self.assertEqual(event.primary_key.integration_outcome_type, "Last Key")

    def test_empty_multi_eventstream(self):
        spec = parse_specification()
        parser = Parser(spec)

        dataset = tablib.Dataset(
            ['1',
             'Test Key', 'Test Value',
             '', '',
             'Last Key', 'Last Value'
             ],
            headers=['unique_id',
                     'integration_outcome_type_first', 'integration_social_first',
                     'integration_outcome_type_secnd', 'integration_social_secnd',
                     'integration_outcome_type', 'integration_social',
                     ]
        )
        events = parser.dataset_to_events(dataset)
        self.assertEqual(len(events), 2)

        event = events[0]
        self.assertEqual(event.value, "Test Value")
        self.assertEqual(event.suffix, "first")
        self.assertEqual(event.primary_key.integration_outcome_type, "Test Key")

        event = events[1]
        self.assertEqual(event.value, "Last Value")
        self.assertEqual(event.suffix, "")
        self.assertEqual(event.primary_key.integration_outcome_type, "Last Key")