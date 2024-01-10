from collections import OrderedDict
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
from openpecha.core.pecha import OpenPechaGitRepo
from ordered_set import OrderedSet
from pandas import DataFrame

from openpecha_data_cataloger.config import CATALOG_DIR, set_environment
from openpecha_data_cataloger.github_token import GITHUB_TOKEN
from openpecha_data_cataloger.utility import (
    download_github_file,
    load_yaml,
    merge_two_dictionary,
)


class Cataloger:
    org = "OpenPecha-Data"
    repo = "catalog"
    file_name = "opf_catalog.csv"

    def __init__(self, token: str):
        self.token = token
        self.base_path = CATALOG_DIR
        self.catalog_path = self.base_path / self.file_name
        self.get_catalog()
        self.catalog = self.load_catalog()
        self.pecha_ids = self.get_catalog_pecha_ids()
        set_environment()

    def get_catalog(self):
        if not self.catalog_path.exists():
            download_github_file(
                token=self.token,
                org=self.org,
                repo_name=self.repo,
                file=self.file_name,
                destination_folder_path=self.catalog_path.parent,
            )

    def load_catalog(self):
        return pd.read_csv(self.catalog_path)

    def get_catalog_pecha_ids(self):
        return self.catalog["Pecha ID"].to_list()

    def load_pechas(self, pecha_ids=None, path: Optional[Path] = None):
        """if pecha_ids is None, load all pechas in catalog"""
        """provide the folder path where pechas are located"""
        if pecha_ids is None:
            pecha_ids = self.pecha_ids
        self.pechas = (self.load_pecha(pecha_id, path) for pecha_id in pecha_ids)

    def load_pecha(self, pecha_id, path=None):
        if path is None:
            pecha_path = None
        else:
            pecha_path = str(path / pecha_id)
        return OpenPechaGitRepo(pecha_id=pecha_id, path=pecha_path)

    def generate_meta_data_report(self) -> DataFrame:
        keys = OrderedSet()
        all_data = []

        for pecha in self.pechas:
            """meta already defined in openpecha toolkit"""
            predefined_metadata = OrderedDict(vars(pecha.meta))
            predefined_metadata = process_metadata_for_enum_names(predefined_metadata)
            """meta from .opf/meta.yml"""
            metadata = OrderedDict(get_meta_data_from_pecha(pecha))
            merged_metadata = merge_two_dictionary(predefined_metadata, metadata)
            all_data.append(merged_metadata)

            # Check if there are any new keys
            new_keys = OrderedSet(predefined_metadata.keys()) - keys
            if new_keys:
                keys.update(new_keys)

        # Creating DataFrame
        df = pd.DataFrame(all_data, columns=keys)
        return df


def process_metadata_for_enum_names(metadata: OrderedDict) -> OrderedDict:
    processed_metadata = OrderedDict()
    for key, value in metadata.items():
        if isinstance(value, Enum):
            processed_metadata[key] = value.name
        else:
            processed_metadata[key] = value
    return processed_metadata


def get_meta_data_from_pecha(pecha: OpenPechaGitRepo):
    """Get metadata from pecha file .opf/meta.yml itself"""
    if pecha.meta_fn.is_file():
        return load_yaml(pecha.meta_fn)


if __name__ == "__main__":
    cataloger = Cataloger(GITHUB_TOKEN)
    cataloger.load_pechas(["P000216", "P000217"])
    df = cataloger.generate_meta_data_report()
    df.to_csv(CATALOG_DIR / "meta_data.csv")
