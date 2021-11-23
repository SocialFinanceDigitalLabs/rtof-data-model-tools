import tablib

from rtofdata.parser import Parser
from rtofdata.specification.parser import parse_specification


def test_null_headers():
    spec = parse_specification()

    parser = Parser(spec)

    data = tablib.Dataset(*[
        ['A', 'User', 'M', 'Test', 'Random'],
        ['B', 'User', 'M', 'Test', 'Random'],
    ], headers=['first_name	', 'last_name', 'gender', None, 'something_else'])

    parser.dataset_to_events(data)