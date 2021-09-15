import unittest

import yaml

from rtofdata.eventstream import StreamParser
from rtofdata.specification.parser import parse_specification


def _yaml_to_stream(input_value):
    stream_data = yaml.safe_load(input_value)
    parser = StreamParser(parse_specification())
    parser.parse_stream(stream_data)
    return parser.records


class TestStreamInsert(unittest.TestCase):

    def test_primary_record(self):
        data = """
- {field: year_of_birth, record: person, value: '1989', primary_key: [DP-14]}
- {field: gender, record: person, value: Woman, primary_key: [DP-14]}
- {field: dispersal_area, record: person, value: Bolton Council, primary_key: [DP-14]}
- {field: date_started_service, record: person, value: 2022-08, primary_key: [DP-14]}
        """

        records = list(_yaml_to_stream(data))
        self.assertEqual(len(records), 1, "List length should be 1")

        r = records[0]
        self.assertEqual(r.get('unique_id'), 'DP-14', 'Expected DP-14')
        self.assertEqual(r.get('year_of_birth'), '1989', 'Expected 1989')
        self.assertEqual(r.get('gender'), 'Woman', 'Expected Woman')
        self.assertEqual(r.get('dispersal_area'), 'Bolton Council', 'Expected Bolton Council')
        self.assertEqual(r.get('date_started_service'), '2022-08', 'Expected 2022-08')

    def test_secondary_record(self):
        data = """
- {field: housing_entry_date, record: housing_entry, value: '2022-10-28', primary_key: [DP-14]}
- {field: housing_entry_accomodation, record: housing_entry, value: RPC, primary_key: [DP-14]}
        """

        records = list(_yaml_to_stream(data))
        self.assertEqual(len(records), 1, "List length should be 1")

        r = records[0]
        self.assertEqual(r.get('unique_id'), 'DP-14', 'Expected DP-14')
        self.assertEqual(r.get('housing_entry_date'), '2022-10-28', 'Expected 2022-10-28')
        self.assertEqual(r.get('housing_entry_accomodation'), 'RPC', 'Expected RPC')

    def test_one_to_many_record(self):
        data = """
- {field: integration_outcome_achieved_date, record: integration_plan, value: '2022-11-29', primary_key: [DP-14, Creation]}
- {field: integration_social, record: integration_plan, value: tbc, primary_key: [DP-14, Creation]}
        """

        records = list(_yaml_to_stream(data))
        self.assertEqual(len(records), 1, "List length should be 1")

        r = records[0]
        self.assertEqual(r.get('unique_id'), 'DP-14', 'Expected DP-14')
        self.assertEqual(r.get('integration_outcome_type'), 'Creation', 'Expected Creation')
        self.assertEqual(r.get('integration_outcome_achieved_date'), '2022-11-29', 'Expected 2022-11-29')
        self.assertEqual(r.get('integration_social'), 'tbc', 'Expected tbc')


if __name__ == '__main__':
    unittest.main()

