import hashlib
import re
from pathlib import Path
import tablib

_ptn_field_id = re.compile(r"[^a-z0-9]")


def pick_value(row_data, **kwargs):
    def _matches(c):
        for key, value in kwargs.items():
            if getattr(c, key) != value:
                return False
        return True

    matches = [c.value for c in row_data if _matches(c)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        return None
    else:
        raise ValueError(f"Multiple matches found: {matches}")


def fix_field_id(field_id):
    if field_id is None:
        return None
    return _ptn_field_id.sub("", field_id.lower())


def file_to_databook(filename: Path):
    if filename.suffix == ".csv":
        with open(filename, 'rt') as fh:
            dataset = tablib.Dataset().load(fh, format="csv")
            return tablib.Databook([dataset])
    elif filename.suffix == ".xlsx":
        with open(filename, 'rb') as fh:
            return tablib.Databook().load(fh, format="xlsx")
    elif filename.suffix == ".xls":
        with open(filename, 'rb') as fh:
            return tablib.Databook().load(fh, format="xls")
    else:
        raise Exception(f"Unknown file type: {filename}")


def file_to_digest(filename: Path):
    with open(filename, 'rb') as fh:
        return hashlib.sha512(fh.read()).hexdigest()


from .parser import Parser
