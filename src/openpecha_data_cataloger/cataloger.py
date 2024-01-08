from openpecha_data_cataloger.config import CATALOG_DIR
from openpecha_data_cataloger.utility import download_github_file


class Cataloger:
    org = "OpenPecha-Data"
    repo = "catalog"
    file_name = "opf_catalog.csv"

    def __init__(self, token: str):
        self.token = token
        self.catalog_path = CATALOG_DIR / self.file_name
        self.get_catalog()

    def get_catalog(self):
        download_github_file(
            token=self.token,
            org=self.org,
            repo_name=self.repo,
            file=self.file_name,
            destination_folder_path=self.catalog_path.parent,
        )


if __name__ == "__main__":
    cataloger = Cataloger(token="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")
