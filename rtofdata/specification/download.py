import logging
import zipfile
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

import requests

REPO_URL = "https://github.com/SocialFinanceDigitalLabs/rtof-data-model/archive/refs"

logger = logging.getLogger(__name__)


def download_spec_version(ref=None, tag=None, target_dir=None, repo_url=REPO_URL):
    if ref is None and tag is None:
        ref = "main"

    if tag:
        url = f"{repo_url}/tags/{tag}.zip"
    else:
        url = f"{repo_url}/heads/{ref}.zip"

    if target_dir is None:
        target_dir = Path(__file__).parent / "../../build/spec"
    else:
        target_dir = Path(target_dir)

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        shutil.rmtree(target_dir)

    with TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        zip_file = temp_dir / "zipfile.zip"
        repo_dir = temp_dir / "repo"

        response = requests.get(url, stream=True)
        with open(zip_file, "wb") as out:
            for chunk in response.iter_content(chunk_size=512 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    out.write(chunk)

        with open(zip_file, "rb") as file:
            with zipfile.ZipFile(file) as zip_ref:
                zip_ref.extractall(repo_dir)

        data_dir = next(repo_dir.glob("**/data"))
        shutil.copytree(data_dir, target_dir)

    logger.info(f"Downloaded specification version {ref} to {target_dir}")
