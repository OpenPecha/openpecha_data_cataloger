from config import PECHAS_DIR

from openpecha_data_cataloger.cataloger import Cataloger


def test_annotation_content_report_generator():
    cataloger = Cataloger()
    cataloger.load_pechas(["P000216", "I1A92E2D9", "P000003"], path=PECHAS_DIR)

    catalog_df = cataloger.generate_annotation_content_report()
    catalog_df.to_csv("test.csv")

    # Function to test a specific pecha, volume, and annotation file
    def test_specific_annotation(
        pecha_id, volume_name, annotation_file_name, expected_values
    ):
        filtered_df = catalog_df[
            (catalog_df["pecha_id"] == pecha_id)
            & (catalog_df["volume_name"] == volume_name)
            & (catalog_df["annotation_file_name"] == annotation_file_name)
        ]

        # Skip test if no data is found
        if filtered_df.empty:
            print(
                f"No data found for {pecha_id}, {volume_name}, {annotation_file_name}. Test skipped."
            )
            return

        row = filtered_df.iloc[0]
        for key, value in expected_values.items():
            assert row[key] == value

    # Define the expected values for each test case
    expected_yigchung = {
        "pecha_id": "P000216",
        "volume_name": "v001",
        "has_base_file": True,
        "annotation_file_name": "Yigchung",
        "is_annotation_file_name_enumed": True,
        "base_fields": ["id", "annotation_type", "revision", "annotations"],
        "undefined_base_fields": [],
        "has_annotation_type": True,
        "annotation_type": "Yigchung",
        "is_annotation_type_enumed": True,
        "has_annotations": True,
        "has_annotation_id_missing": False,
        "annotation_fields": ["span"],
        "has_annotation_field_validation_error": False,
        "required_annotation_fields": ["span"],
        "missing_annotation_fields": [],
        "extra_annotation_fields": [],
        "has_span_annotation": True,
        "has_start_end_in_span": True,
        "start_end_are_integer": {},
        "start_greater_equal_than_end": {
            "3e92bdc162b444fe96f12703fa880f0a": {
                "span": {"start": 189353, "end": 189353}
            }
        },
        "start_end_negative_values": {},
        "start_end_greater_than_base_file_length": {},
    }

    expected_author = {
        "has_base_file": True,
        "is_annotation_type_enumed": True,
        "is_annotation_file_name_enumed": True,
        "has_annotations": True,
        "has_annotation_id_missing": True,
    }

    expected_quotation = {
        "has_base_file": True,
        "is_annotation_type_enumed": False,
        "has_annotations": True,
    }
    expected_segment = {
        "volume_name": "ABFB",
        "annotation_type": "Segment",
        "is_annotation_type_enumed": True,
        "has_annotation_id_missing": False,
    }

    expected_P000003_res = {
        "has_base_file": True,
        "is_annotation_file_name_enumed": False,
        "base_fields": ["id", "annotation_type", "rev", "content"],
        "undefined_base_fields": ["rev", "content"],
        "annotation_type": "pagination",
        "is_annotation_type_enumed": False,
        "has_annotations": False,
    }

    # Run the tests
    test_specific_annotation("P000216", "v001", "Yigchung", expected_yigchung)
    test_specific_annotation("P000216", "v001", "Author", expected_author)
    test_specific_annotation("P000216", "v001", "Quotation", expected_quotation)
    test_specific_annotation("I1A92E2D9", "ABFB", "Segment", expected_segment)
    test_specific_annotation("P000003", "v001", "pagination", expected_P000003_res)


test_annotation_content_report_generator()
