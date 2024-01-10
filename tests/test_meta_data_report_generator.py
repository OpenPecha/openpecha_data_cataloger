from config import PECHAS_DIR

from openpecha_data_cataloger.cataloger import Cataloger
from openpecha_data_cataloger.config import set_environment
from openpecha_data_cataloger.github_token import GITHUB_TOKEN


def test_meta_data_report_generator():
    set_environment()
    cataloger = Cataloger(GITHUB_TOKEN)
    cataloger.load_pechas(["P000216"], path=PECHAS_DIR)

    catalog_df = cataloger.generate_meta_data_report()
    P000216 = catalog_df[catalog_df["id"] == "P000216"]
    assert P000216["initial_creation_type"].iloc[0] == "ebook"
    assert P000216["created_at"].iloc[0] == "31/01/2020"
    assert P000216["last_modified_at"].iloc[0] == "25/11/2021"

    P000216_source_metadata = P000216["source_metadata"].iloc[0]
    expected_title = "༄༅། །ངེས་ཤེས་རིན་པོ་ཆེའི་སྒྲོན་མེའི་ཚིག་གི་དོན་གསལ་བའི་འགྲེལ་ཆུང་བློ་གྲོས་སྣང་བའི་སྒོ་འབྱེད་ཅེས་བྱ་བ་བཞུགས་སོ། །"  # noqa
    assert P000216_source_metadata["title"] == expected_title
    assert P000216_source_metadata["authors"] == ["མཛད་པ་པོ། མཁན་པོ་ཀུན་དཔལ།"]
    assert P000216_source_metadata["layers"] == [
        "book_title",
        "author",
        "chapter_title",
        "quotation",
        "sabche",
        "yigchung",
    ]
    assert P000216_source_metadata["id"] == "LEK-PHI-059-1-1"
    """web data was not included in PechaMetadata from toolkit"""

    P000216_web_metadata = P000216["web_metadata"].iloc[0]
    expected_english_title = "Unlocking the Light of Intellegence:A Short Commentary on Mipham's Beacon of Certainty"  # noqa
    expected_tibetan_title = "ངེས་ཤེས་རིན་པོ་ཆེའི་སྒྲོན་མེའི་ཚིག་གི་དོན་གསལ་བའི་འགྲེལ་ཆུང་བློ་གྲོས་སྣང་བའི་སྒོ་འབྱེད་ཅེས་བྱ་བ་བཞུགས་སོ།།"  # noqa

    assert P000216_web_metadata["title"]["en"] == expected_english_title
    assert P000216_web_metadata["title"]["bo"] == expected_tibetan_title

    assert P000216_web_metadata["author"]["en"] == "Khenpo Kunpal"
    assert P000216_web_metadata["author"]["bo"] == "མཁན་པོ་ཀུན་དཔལ།"
    assert P000216_web_metadata["website"] == "http://dharmacloud.tsadra.org"
    expected_english_collection = "Lekshey Ling Philosophy Series–  Book 59-1"
    expected_tibetan_collection = "ལེགས་བཤད་གླིང་རིགས་པའི་གཞུང་ལུགས།–  དེབ། ༥༩ – ༡"
    assert P000216_web_metadata["collection"]["en"] == expected_english_collection
    assert P000216_web_metadata["collection"]["bo"] == expected_tibetan_collection
