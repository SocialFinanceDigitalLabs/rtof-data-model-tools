import unittest

import tablib

from rtofdata.parser import pick_value, fix_field_id


class TestParser(unittest.TestCase):

    def test_pick_value(self):
        data = [
            dict(a=1, b=1, value='a'),
            dict(a=1, b=2, value='b'),
            dict(a=3, b=3, value='c'),
            dict(a=4, b=3, value='d'),
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
