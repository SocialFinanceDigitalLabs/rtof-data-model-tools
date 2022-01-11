import tablib

from rtofdata.parser import Parser


def test_null_headers(specification):
    parser = Parser(specification)

    data = tablib.Dataset(*[
        ['A', 'User', 'M', 'Test', 'Random'],
        ['B', 'User', 'M', 'Test', 'Random'],
    ], headers=['first_name	', 'last_name', 'gender', None, 'something_else'])

    parser.dataset_to_events(data)