from dataclasses import dataclass, field
from typing import List, Optional

from openpecha.core.layer import LayerEnum

from openpecha_data_cataloger.config import (
    ALL_LAYERS_ENUM_VALUES,
    BASE_ANNOTATION_FEATURES,
)


@dataclass
class AnnotationCataloger:
    pecha_id: str
    volume_name: str
    layer: Optional[LayerEnum] = None
    has_base_file: bool = False
    annotation_file_name: Optional[str] = None
    is_annotation_file_name_enumed: Optional[bool] = False
    base_fields: List[str] = field(default_factory=list)
    undefined_base_fields: List[str] = field(default_factory=list)
    has_annotation_type: Optional[bool] = False
    annotation_type: Optional[str] = None
    is_annotation_type_enumed: Optional[bool] = False
    has_annotations: Optional[bool] = None

    def __init__(
        self,
        pecha_id,
        volume_name,
        annotation_content: Optional[dict] = None,
        layer: Optional[LayerEnum] = None,
    ):
        self.pecha_id = pecha_id
        self.volume_name = volume_name
        self.layer = layer
        self.annotation_content = annotation_content
        self.load_fields()

    def load_fields(self):
        if self.layer:
            self.has_base_file = True
            self.is_annotation_file_name_enumed = True
        if self.annotation_content is not None:
            self.load_annotation_content_related_fields()

    def load_annotation_content_related_fields(self):
        if self.annotation_content is None:
            return
        self.has_base_file = True
        self.base_fields = list(self.annotation_content.keys())
        self.undefined_base_fields = list(
            set(self.annotation_content.keys()) - set(BASE_ANNOTATION_FEATURES)
        )

        annotation_type = self.annotation_content.get("annotation_type")
        if annotation_type is not None:
            self.annotation_file_name = annotation_type
            self.has_annotation_type = True
            self.annotation_type = annotation_type
            self.is_annotation_type_enumed = annotation_type in ALL_LAYERS_ENUM_VALUES
            self.has_annotations = "annotations" in self.annotation_content
