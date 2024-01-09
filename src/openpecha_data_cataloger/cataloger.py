import csv
from collections import OrderedDict
from typing import List, Optional

from openpecha.core.pecha import OpenPechaGitRepo
from ordered_set import OrderedSet

from openpecha_data_cataloger.config import CATALOG_DIR, set_environment
from openpecha_data_cataloger.github_token import GITHUB_TOKEN
from openpecha_data_cataloger.utility import (
    download_github_file,
    load_yaml,
    merge_two_dictionary,
    rewrite_csv,
    write_header_to_csv,
    write_to_csv,
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
        self.pecha_ids = self.get_catalog_pecha_names()
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
        with open(self.catalog_path, newline="") as csvfile:
            catalog = csv.DictReader(csvfile)
            return list(catalog)

    def get_catalog_pecha_names(self):
        return [row["Pecha ID"] for row in self.catalog]

    def load_pechas(self, pecha_ids=None):
        if pecha_ids is None:
            pecha_ids = self.pecha_ids
        self.pechas = (self.load_pecha(pecha_id) for pecha_id in pecha_ids)

    def load_pecha(self, pecha_id):
        return OpenPechaGitRepo(pecha_id=pecha_id)

    def generate_folder_structure_report(self):
        output_file = self.base_path / "folder_structure.csv"
        keys = OrderedSet(
            ["Pecha ID", "contains annotations", "volume counts", "Layer names"]
        )
        write_header_to_csv(output_file, keys)
        for pecha in self.pechas:
            curr_row = OrderedDict()
            curr_row["Pecha ID"] = pecha.pecha_id
            curr_row["contains annotations"] = "Yes" if pecha.components else "No"
            curr_row["volume counts"] = len(pecha.components)
            curr_row["Layer names"] = get_layer_names_from_pecha(pecha)

            write_to_csv(output_file, keys, [curr_row])

    def generate_meta_data_report(self):
        keys = OrderedSet()
        temp_data = []
        output_file = self.base_path / "meta_data.csv"

        for pecha in self.pechas:
            """meta already defined in openpecha toolkit"""
            predefined_metadata = OrderedDict(vars(pecha.meta))
            """meta from .opf/meta.yml"""
            metadata = OrderedDict(get_meta_data_from_pecha(pecha))
            merged_metadata = merge_two_dictionary(predefined_metadata, metadata)
            temp_data.append(merged_metadata)

            # Check if there are any new keys
            new_keys = OrderedSet(predefined_metadata.keys()) - keys
            if new_keys:
                keys.update(new_keys)
                rewrite_csv(output_file, keys, temp_data)
                temp_data = []

        # Final write if not already done
        if temp_data:
            write_to_csv(output_file, keys, temp_data)


def get_meta_data_from_pecha(pecha: OpenPechaGitRepo):
    """Get metadata from pecha file .opf/meta.yml itself"""
    if pecha.meta_fn.is_file():
        return load_yaml(pecha.meta_fn)


def get_layer_names_from_pecha(pecha: OpenPechaGitRepo) -> Optional[List]:
    """Get layer names from pecha file .opf/meta.yml itself"""
    if not pecha.components:
        return None
    return [layer.value for vol, layers in pecha.components.items() for layer in layers]


if __name__ == "__main__":
    cataloger = Cataloger(GITHUB_TOKEN)
    cataloger.load_pechas(["P000216", "P000217"])
    cataloger.generate_folder_structure_report()
