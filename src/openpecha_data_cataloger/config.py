import os
from pathlib import Path

from openpecha.core.layer import LayerEnum
from ordered_set import OrderedSet


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


def set_environment():
    """fetch github token from environment variable"""
    os.environ["GITHUB_TOKEN"] = "github_token"
    os.environ["OPENPECHA_DATA_GITHUB_ORG"] = "OpenPecha-Data"
    os.environ["GITHUB_USERNAME"] = "tenzin3"


ROOT_DIR = Path(__file__).parent.parent.parent
CATALOG_DIR = _mkdir(ROOT_DIR / ".catalog")

BASE_ANNOTATION_FEATURES = ["id", "annotation_type", "revision", "annotations"]
ALL_LAYERS_ENUM_VALUES = [layer.value for layer in LayerEnum]


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
        "annotation file name",
        "is annotation file name enumed",
        "base fields",
        "undefined base fields",
        "has annotation_type",
        "annotation_type",
        "is annotation_type enumed",
        "has annotations",
    ]
)
