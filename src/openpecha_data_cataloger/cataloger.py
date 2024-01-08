import csv
from collections import OrderedDict

from openpecha.core.pecha import OpenPechaGitRepo
from ordered_set import OrderedSet

from openpecha_data_cataloger.config import CATALOG_DIR, set_environment
from openpecha_data_cataloger.github_token import GITHUB_TOKEN
from openpecha_data_cataloger.utility import (
    download_github_file,
    rewrite_csv,
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

    def generate_meta_data_report(self):
        keys = OrderedSet()
        temp_data = []
        output_file = self.base_path / "meta_data.csv"

        for pecha in self.pechas:
            # Collect pecha metadata
            metadata = OrderedDict(vars(pecha.meta))
            temp_data.append(metadata)

            # Check if there are any new keys
            new_keys = OrderedSet(metadata.keys()) - keys
            if new_keys:
                keys.update(new_keys)
                rewrite_csv(output_file, keys, temp_data)
                temp_data = []

        # Final write if not already done
        if temp_data:
            write_to_csv(output_file, keys, temp_data)


if __name__ == "__main__":
    cataloger = Cataloger(GITHUB_TOKEN)
    cataloger.load_pechas(["P000216", "P000217"])
    cataloger.generate_meta_data_report()
