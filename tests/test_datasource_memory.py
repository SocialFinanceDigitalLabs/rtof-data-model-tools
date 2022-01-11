from rtofdata.datasource.in_memory import InMemoryDataSource
from rtofdata.parser.parser import DataEvent


def _gen_event(spec, record_id, field_id, value, **primary_keys):
    pk = spec.record_by_id(record_id).get_key(**primary_keys)
    return DataEvent(
        record=record_id,
        field=field_id,
        value=value,
        primary_key=pk
    )


def test_basic_to_eventstream(specification):
    events = [
        _gen_event(specification, "person", "year_of_birth", "1989", unique_id="DP-14"),
        _gen_event(specification, "person", "gender", "Woman", unique_id="DP-14"),
    ]

    ds = InMemoryDataSource(specification)
    for e in events:
        ds.update(e)

    expected_result = dict(unique_id="DP-14", year_of_birth="1989", gender="Woman")
    actual_result = ds.get_single_record("person", "DP-14")._asdict()
    assert actual_result == actual_result | expected_result

    ds.update(_gen_event(specification, "person", "gender", "Man", unique_id="DP-14"))

    expected_result = dict(unique_id="DP-14", year_of_birth="1989", gender="Man")
    actual_result = ds.get_single_record("person", "DP-14")._asdict()
    assert actual_result == actual_result | expected_result
