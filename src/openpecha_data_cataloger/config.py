import os
from pathlib import Path

from ordered_set import OrderedSet


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


def set_environment():
    """fetch github token from environment variable"""
    os.environ["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN", "your_default_token")
    os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
    os.environ["GITHUB_USERNAME"] = "tenzin3"


ROOT_DIR = Path(__file__).parent.parent.parent
CATALOG_DIR = _mkdir(ROOT_DIR / ".catalog")


FOLDER_STRUCTURE_KEYS = OrderedSet(
    [
        "id",
        "contains index",
        "contains annotations",
        "volume count",
        "volumes",
        "unenumed volumes",
    ]
)
ANNOTATION_CONTENT_KEYS = OrderedSet(
    [
        "pecha id",
        "volume name",
        "has base file",
        "layer name",
        "is layer enumed",
        "base fields",
        "undefined base fields",
    ]
)
