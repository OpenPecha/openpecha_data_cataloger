import os
from pathlib import Path

from openpecha_data_cataloger.github_token import GITHUB_TOKEN


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


def set_environment():
    os.environ["GITHUB_TOKEN"] = GITHUB_TOKEN
    os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
    os.environ["GITHUB_USERNAME"] = "gangagyatso4364"


ROOT_DIR = Path(__file__).parent.parent.parent
CATALOG_DIR = _mkdir(ROOT_DIR / ".catalog")
