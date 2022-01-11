from rtofdata.validation import get_validator


def test_get_validator():
    validator = get_validator('required')
    assert validator is not None