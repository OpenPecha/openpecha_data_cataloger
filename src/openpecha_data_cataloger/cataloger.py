from collections import OrderedDict
from enum import Enum
from pathlib import Path
from typing import Optional

import pandas as pd
from openpecha.core.layer import LayerEnum
from openpecha.core.pecha import OpenPechaGitRepo
from ordered_set import OrderedSet
from pandas import DataFrame

from openpecha_data_cataloger.config import CATALOG_DIR, set_environment
from openpecha_data_cataloger.utility import (
    download_github_file,
    load_yaml,
    merge_two_dictionary,
)

BASE_ANNOTATION_FEATURES = ["id", "annotation_type", "revision", "annotations"]


class Cataloger:
    org = "OpenPecha-Data"
    repo = "catalog"
    file_name = "opf_catalog.csv"

    def __init__(self):
        self.base_path = CATALOG_DIR
        self.catalog_path = self.base_path / self.file_name
        set_environment()

    def get_catalog(self, token: str):
        if not self.catalog_path.exists():
            download_github_file(
                token=token,
                org=self.org,
                repo_name=self.repo,
                file=self.file_name,
                destination_folder_path=self.catalog_path.parent,
            )
        self.catalog = self.load_catalog()
        self.pecha_ids = self.get_catalog_pecha_ids()

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
            return OpenPechaGitRepo(pecha_id=pecha_id)

        pecha_path = str(path / pecha_id)
        return OpenPechaGitRepo(pecha_id=pecha_id, path=pecha_path)

    def generate_annotation_content_report(self):
        keys = OrderedSet(
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
        all_data = []

        for pecha in self.pechas:
            for volume, layers in pecha.components.items():
                curr_row = OrderedDict()
                if volume not in pecha.base_names_list:
                    curr_row = OrderedDict(
                        [
                            ("pecha id", pecha.pecha_id),
                            ("volume", volume),
                            ("has base file", "No"),
                        ]
                    )
                    all_data.append(curr_row)
                    continue
                for layer in layers:
                    curr_row = OrderedDict()
                    annotation_content = pecha.read_layers_file(
                        base_name=volume, layer_name=layer
                    )
                    curr_row["pecha id"] = pecha.pecha_id
                    curr_row["volume name"] = volume
                    curr_row["has base file"] = "Yes"
                    curr_row["layer name"] = annotation_content["annotation_type"]
                    curr_row["is layer enumed"] = "Yes"
                    curr_row["base fields"] = list(annotation_content.keys())
                    curr_row["undefined base fields"] = list(
                        set(annotation_content.keys()) - set(BASE_ANNOTATION_FEATURES)
                    )
                    all_data.append(curr_row)
                """layer that are not enumed in LayerEnum"""
                enum_layers = get_unenumed_layer_names_from_pecha(pecha)
                if enum_layers:
                    for layer_name in enum_layers[volume]:
                        curr_row = OrderedDict()
                        layer_fn = pecha.layers_path / volume / f"{layer_name}.yml"
                        annotation_content = load_yaml(layer_fn)
                        curr_row["pecha id"] = pecha.pecha_id
                        curr_row["volume"] = volume
                        curr_row["has base file"] = "Yes"
                        curr_row["layer name"] = layer_name
                        curr_row["is layer enumed"] = "No"
                        curr_row["base fields"] = list(annotation_content.keys())
                        curr_row["undefined base fields"] = list(
                            set(annotation_content.keys())
                            - set(BASE_ANNOTATION_FEATURES)
                        )
                        all_data.append(curr_row)
        # Convert the list of OrderedDict to a Pandas DataFrame
        df = pd.DataFrame(all_data, columns=keys)
        return df

    def generate_folder_structure_report(self):
        keys = OrderedSet(
            [
                "id",
                "contains index",
                "contains annotations",
                "volume count",
                "volumes",
                "unenumed volumes",
            ]
        )
        all_data = []

        for pecha in self.pechas:
            curr_row = OrderedDict()
            curr_row["id"] = pecha.pecha_id
            curr_row["contains index"] = "Yes" if pecha.index else "No"

            try:
                curr_row["contains annotations"] = "Yes" if pecha.components else "No"
                curr_row["volume count"] = len(pecha.components)
                curr_row["volumes"] = get_layer_names_from_pecha(pecha)
                curr_row["unenumed volumes"] = get_unenumed_layer_names_from_pecha(
                    pecha
                )
            except FileNotFoundError:
                curr_row["contains annotations"] = "No"
                curr_row["volume count"] = 0
                curr_row["volumes"] = None
                curr_row["unenumed volumes"] = None

            all_data.append(curr_row)

        # Convert the list of OrderedDict to a Pandas DataFrame
        df = pd.DataFrame(all_data, columns=keys)
        return df

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


def get_layer_names_from_pecha(pecha: OpenPechaGitRepo) -> Optional[OrderedDict]:
    """Get layer names from OpenPechaGitRepo object"""
    if not pecha.components:
        return None
    res = OrderedDict()
    for vol, layers in pecha.components.items():
        res[vol] = [layer.name for layer in layers]
    return res


def get_unenumed_layer_names_from_pecha(
    pecha: OpenPechaGitRepo,
) -> Optional[OrderedDict]:
    """Get all layer names from .opf/layers it self object"""
    if not pecha.components:
        return None

    res = OrderedDict()
    all_layers = {layer.value for layer in LayerEnum}
    for vol_dir in pecha.layers_path.iterdir():
        # Collect layer names where its enum is not in LayerEnum
        res[vol_dir.name] = [
            fn.stem for fn in vol_dir.iterdir() if fn.stem not in all_layers
        ]
    return res


if __name__ == "__main__":
    cataloger = Cataloger()
    cataloger.load_pechas(pecha_ids=["P000216"])
    df = cataloger.generate_annotation_content_report()
    df.to_csv(CATALOG_DIR / "annotation_content_report.csv")
