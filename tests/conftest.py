from pathlib import Path

from rtofdata.specification.parser import parse_specification
from rtofdata import config

import pytest

from rtofdata.specification import download


@pytest.fixture()
def specification():
    config.data_root = (Path(__name__).parent / "../build/specification").absolute()
    if not config.data_dir.exists():
        download.download_spec_version(target_dir=config.data_dir)
    return parse_specification()
