import csv

from openpecha_data_cataloger.config import CATALOG_DIR
from openpecha_data_cataloger.github_token import GITHUB_TOKEN
from openpecha_data_cataloger.utility import download_github_file


class Cataloger:
    org = "OpenPecha-Data"
    repo = "catalog"
    file_name = "opf_catalog.csv"

    def __init__(self, token: str):
        self.token = token
        self.catalog_path = CATALOG_DIR / self.file_name
        self.get_catalog()
        self.catalog = self.load_catalog()

    def get_catalog(self):
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


if __name__ == "__main__":
    cataloger = Cataloger(token=GITHUB_TOKEN)
    print(cataloger.catalog)
