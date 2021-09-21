import unittest
from pathlib import Path
from rtofdata.parser import pick_value, fix_field_id, file_to_databook, Parser
from rtofdata.specification.parser import parse_specification

class _MyClass:

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestParserUtil(unittest.TestCase):

    def assertFieldResult(self, result, field_id, record_id, suffix=""):
        self.assertEqual(result[0].field.id, field_id)
        self.assertEqual(result[0].record.id, record_id)
        self.assertEqual(result[1], suffix)

    def test_pick_value(self):
        data = [
            _MyClass(a=1, b=1, value='a'),
            _MyClass(a=1, b=2, value='b'),
            _MyClass(a=3, b=3, value='c'),
            _MyClass(a=4, b=3, value='d'),
        ]

        self.assertEqual(pick_value(data, a=3), 'c')

        with self.assertRaises(ValueError):
            pick_value(data, a=1)

        self.assertEqual(pick_value(data, a=1, b=1), 'a')
        self.assertEqual(pick_value(data, a=1, b=2), 'b')

    def test_fix_field_id_simple(self):
        self.assertEqual(fix_field_id('boo'), 'boo')

    def test_fix_field_id_spaces(self):
        self.assertEqual(fix_field_id('b o o'), 'boo')

    def test_fix_field_id_caps(self):
        self.assertEqual(fix_field_id('BooYa'), 'booya')

    def test_fix_field_id_chars(self):
        self.assertEqual(fix_field_id('a-b?c&d_5"e'), 'abcd5e')

    def test_fix_field_id_realistic(self):
        self.assertEqual(fix_field_id('Unique ID'), fix_field_id('unique_id'))

    def test_load_csv(self):
        db = file_to_databook(Path(__file__).parent / "files/parser_sample_1.csv")
        self.assertEqual(len(db.sheets()), 1, "Excepting 1 sheet")
        sheet = db.sheets()[0]
        self.assertListEqual(sheet.headers, ['unique_id', 'year_of_birth', 'gender',
                                             'dispersal_area', 'date_started_service'])
        self.assertEqual(len(sheet), 6, "Expecting 6 rows")

    def _check_sheet(self, db):
        self.assertEqual(len(db.sheets()), 2, "Excepting 2 sheets")
        sheet = db.sheets()[0]
        self.assertListEqual(sheet.headers, ['unique_id', 'year_of_birth', 'gender',
                                             'dispersal_area', 'date_started_service'])
        self.assertEqual(len(sheet), 6, "Expecting 6 rows")

        sheet = db.sheets()[1]
        self.assertListEqual(sheet.headers, ['unique_id', 'year_of_birth', 'gender',
                                             'dispersal_area', 'date_started_service'])
        self.assertEqual(len(sheet), 6, "Expecting 6 rows")

    def test_load_xlsx(self):
        db = file_to_databook(Path(__file__).parent / "files/parser_sample_1.xlsx")
        self._check_sheet(db)

    @unittest.skip("tablib seems to have an issue with xls files")
    def test_load_xls(self):
        db = file_to_databook(Path(__file__).parent / "files/parser_sample_1.xls")
        self._check_sheet(db)

    def test_field_by_id(self):
        spec = parse_specification()
        parser = Parser(spec)

        self.assertFieldResult(parser.get_by_field_id('unique_id'), 'unique_id', 'person')
        self.assertFieldResult(parser.get_by_field_id('unique_id_52'), 'unique_id', 'person', "52")
