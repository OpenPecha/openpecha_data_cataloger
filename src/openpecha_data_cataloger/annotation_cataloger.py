from dataclasses import dataclass, field
from typing import Dict, List, Optional

from openpecha.core.layer import LayerEnum, _get_annotation_class
from ordered_set import OrderedSet

from openpecha_data_cataloger.config import (
    ALL_LAYERS_ENUM_VALUES,
    BASE_ANNOTATION_FEATURES,
)


@dataclass
class AnnotationCataloger:
    pecha_id: str
    layer: Optional[LayerEnum] = None
    has_base_file: bool = False
    annotation_file_name: Optional[str] = None
    is_annotation_file_name_enumed: Optional[bool] = False
    base_fields: List[str] = field(default_factory=list)
    undefined_base_fields: List[str] = field(default_factory=list)
    has_annotation_type: Optional[bool] = False
    annotation_type: Optional[str] = None
    is_annotation_type_enumed: Optional[bool] = False
    has_annotations: Optional[bool] = False
    """'annotations'and 'base file length' not included in the report"""
    base_file_length: int = -1
    annotations: Optional[Dict] = field(default_factory=dict)
    """check if annotations is a list of dict or dict of dict"""
    has_annotation_id_missing: Optional[bool] = False
    annotation_fields: List = field(default_factory=list)
    """check if an obj can be instantiated with _get_annotation_class"""
    has_annotation_field_validation_error: bool = False
    """from using _get_annotation_class"""
    required_annotation_fields: List = field(default_factory=list)
    missing_annotation_fields: List = field(default_factory=list)
    extra_annotation_fields: List = field(default_factory=list)
    has_span_annotation: Optional[bool] = False
    has_start_end_in_span: Optional[bool] = False
    start_end_are_integer: Optional[dict] = field(default_factory=dict)
    start_greater_equal_than_end: Dict = field(default_factory=dict)
    start_end_negative_values: Dict = field(default_factory=dict)
    start_end_greater_than_base_file_length: Dict = field(default_factory=dict)

    def __init__(
        self,
        pecha_id,
        volume_name,
        annotation_content: Optional[dict] = None,
        base_file_length: Optional[int] = None,
        layer: Optional[LayerEnum] = None,
    ):
        self.pecha_id = pecha_id
        self.volume_name = volume_name
        self.annotation_content = annotation_content
        if base_file_length is not None:
            self.base_file_length = base_file_length
        self.layer = layer
        self.load_fields()

    def load_fields(self):
        if self.layer:
            self.is_annotation_file_name_enumed = True
        if self.annotation_content is not None:
            self.process_annotation_content()

    def process_annotation_content(self):
        if self.annotation_content is None:
            return
        self.has_base_file = True
        self.base_fields = list(self.annotation_content.keys())
        self.undefined_base_fields = list(
            OrderedSet(self.base_fields) - OrderedSet(BASE_ANNOTATION_FEATURES)
        )
        self.process_annotation_type()
        self.process_annotations()

    def process_annotation_type(self):
        if self.annotation_content is None:
            return
        annotation_type = self.annotation_content.get("annotation_type")
        if annotation_type:
            self.set_annotation_type_details(annotation_type)

    def set_annotation_type_details(self, annotation_type):
        self.annotation_file_name = annotation_type
        self.has_annotation_type = True
        self.annotation_type = annotation_type
        self.is_annotation_type_enumed = annotation_type in ALL_LAYERS_ENUM_VALUES

    def process_annotations(self):

        if (
            self.annotation_content is None
            or "annotations" not in self.annotation_content
        ):
            return
        self.has_annotations = True
        annotations = self.annotation_content["annotations"]
        if isinstance(annotations, list):
            self.has_annotation_id_missing = True
            self.annotations = merge_list_of_dicts(annotations)
        else:
            self.annotations = annotations
        self.analyze_annotation_fields()

    def analyze_annotation_fields(self):
        if self.annotations is None or self.annotations == {}:
            return
        first_annotation = next(iter(self.annotations.values()))
        self.process_span_annotation(first_annotation)
        if first_annotation:
            self.annotation_fields = list(first_annotation.keys())
        if self.layer:
            self.compare_with_required_fields(first_annotation)

    def process_span_annotation(self, annotation):
        if annotation is None:
            return
        self.has_span_annotation = "span" in annotation
        if self.has_span_annotation:
            if "start" in annotation["span"] and "end" in annotation["span"]:
                self.has_start_end_in_span = True
                self.analyze_start_end_in_annotation_spans()

    def analyze_start_end_in_annotation_spans(self):
        if self.annotations is None:
            return
        self.start_greater_equal_than_end = {}
        self.start_end_negative_values = {}
        self.start_end_greater_than_base_file_length = {}
        self.start_end_are_integer = {}
        for annotation_id, annotation in self.annotations.items():
            if "start" in annotation["span"] and "end" in annotation["span"]:
                start, end = annotation["span"]["start"], annotation["span"]["end"]
                if not isinstance(start, int) or not isinstance(end, int):
                    self.start_end_are_integer[annotation_id] = annotation
                    continue
                if start >= end:
                    self.start_greater_equal_than_end[annotation_id] = annotation
                if start < 0 or end < 0:
                    self.start_end_negative_values[annotation_id] = annotation
                if start > self.base_file_length or end > self.base_file_length:
                    self.start_end_greater_than_base_file_length[
                        annotation_id
                    ] = annotation

    def compare_with_required_fields(self, first_annotation: Dict):
        base_class = _get_annotation_class(self.layer)
        fields = base_class.__fields__
        try:
            base_class.parse_obj(first_annotation)
            self.has_annotation_field_validation_error = False
        except:  # noqa
            self.has_annotation_field_validation_error = True

        self.required_annotation_fields = [
            name for name, field_info in fields.items() if field_info.required
        ]
        self.missing_annotation_fields = [
            name
            for name in self.required_annotation_fields
            if name not in self.annotation_fields
        ]
        self.extra_annotation_fields = [
            name
            for name in self.annotation_fields
            if name not in self.required_annotation_fields
        ]


def merge_list_of_dicts(list_of_dicts: List[dict]) -> dict:
    return {idx: item for idx, item in enumerate(list_of_dicts)}
