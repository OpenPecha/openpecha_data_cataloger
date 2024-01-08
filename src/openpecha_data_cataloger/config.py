from pathlib import Path


def _mkdir(path):
    if path.is_dir():
        return path
    path.mkdir(exist_ok=True, parents=True)
    return path


ROOT_DIR = Path(__file__).parent.parent.parent
CATALOG_DIR = _mkdir(ROOT_DIR / ".catalog")
