from collections import OrderedDict

from config import PECHAS_DIR

from openpecha_data_cataloger.cataloger import Cataloger


def test_folder_structure_report_generator():
    cataloger = Cataloger()
    cataloger.load_pechas(["P000216", "I1A92E2D9", "O869F9D37"], path=PECHAS_DIR)

    catalog_df = cataloger.generate_folder_structure_report()
    P000216 = catalog_df[catalog_df["id"] == "P000216"]
    assert P000216["contains index"].iloc[0] == "No"
    assert P000216["contains annotations"].iloc[0] == "Yes"
    assert P000216["volume count"].iloc[0] == 1
    expected_volumes = OrderedDict(
        [("v001", ["yigchung", "author", "book_title", "chapter", "sabche"])]
    )

    for key in P000216["volumes"].iloc[0]:
        assert sorted(P000216["volumes"].iloc[0][key]) == sorted(expected_volumes[key])
    assert P000216["unenumed volumes"].iloc[0] == OrderedDict([("v001", ["Quotation"])])

    I1A92E2D9 = catalog_df[catalog_df["id"] == "I1A92E2D9"]
    assert I1A92E2D9["contains index"].iloc[0] == "Yes"
    assert I1A92E2D9["contains annotations"].iloc[0] == "Yes"
    assert I1A92E2D9["volume count"].iloc[0] == 1
    assert I1A92E2D9["volumes"].iloc[0] == OrderedDict([("ABFB", ["segment"])])
    assert I1A92E2D9["unenumed volumes"].iloc[0] == OrderedDict([("ABFB", [])])

    O869F9D37 = catalog_df[catalog_df["id"] == "O869F9D37"]
    assert O869F9D37["contains index"].iloc[0] == "No"
    assert O869F9D37["contains annotations"].iloc[0] == "No"
    assert O869F9D37["volume count"].iloc[0] == 0
    assert O869F9D37["volumes"].iloc[0] is None
    assert O869F9D37["unenumed volumes"].iloc[0] is None


test_folder_structure_report_generator()
