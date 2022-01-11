from pathlib import Path

from rtofdata.specification.parser import parse_specification
from rtofdata import config

import pytest

from rtofdata.specification import download


@pytest.fixture()
def specification():
    spec_dir = Path(__name__).parent / "../build/specification"
    config.data_root = spec_dir.absolute()
    download.download_spec_version(target_dir=spec_dir / "data")
    return parse_specification()
