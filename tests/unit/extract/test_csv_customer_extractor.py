import pytest

from customer_data_platform.exceptions.extraction import ExtractionError

from customer_data_platform.extract import csv_extractor
from customer_data_platform.models.raw_customer import RawCustomer


def create_csv(tmp_path, content: str):
    csv_file = tmp_path / "customers.csv"
    csv_file.write_text(content, encoding="utf-8")
    return csv_file


def test_extract_returns_customers(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """customer_id,name,email,country
1,John,john@abc.de,germany
2,Jane,jane@d.de,ireland
""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)
    expected_result = [
        RawCustomer("1", name="John", email="john@abc.de", country="germany"),
        RawCustomer("2", name="Jane", email="jane@d.de", country="ireland"),
    ]
    assert extractor.extract() == expected_result


def test_extract_returns_empty_list_for_empty_csv(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)
    with pytest.raises(ExtractionError):
        extractor.extract()


def test_extract_raises_if_file_missing(tmp_path):
    extractor = csv_extractor.CsvCustomerExtractor("non_existing_file.csv")

    with pytest.raises(ExtractionError):
        extractor.extract()


def test_missing_column(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """customer_id,name
1,John
""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)

    with pytest.raises(ExtractionError):
        extractor.extract()


def test_extract_handles_empty_cells(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """customer_id,name,email,country
1,John,john@abc.de,
""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)
    expected_result = [
        RawCustomer("1", name="John", email="john@abc.de", country=""),
    ]
    assert extractor.extract() == expected_result


def test_extract_ignores_extra_columns(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """customer_id,name,email,country,nickname
1,John,john@abc.de,germany,j
""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)
    expected_result = [
        RawCustomer("1", name="John", email="john@abc.de", country="germany"),
    ]
    assert extractor.extract() == expected_result


def test_extract_is_independent_of_column_order(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """customer_id,email,name,country
1,john@abc.de,John,germany,j
""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)
    expected_result = [
        RawCustomer("1", name="John", email="john@abc.de", country="germany"),
    ]
    assert extractor.extract() == expected_result


def test_extract_reads_utf8_characters(tmp_path):
    csv_file = create_csv(
        tmp_path,
        """customer_id,email,name,country
1,john@abc.de,Jöhn Müller,germany
2,maria@abc.de,Mariá García,spain
""",
    )

    extractor = csv_extractor.CsvCustomerExtractor(csv_file)

    result = extractor.extract()

    assert result[0].name == "Jöhn Müller"
    assert result[1].name == "Mariá García"


def test_extract_fails_if_file_is_not_csv(tmp_path):
    txt_file = tmp_path / "data.txt"

    txt_file.write_text(
        "this is not a csv file\njust plain text",
        encoding="utf-8",
    )

    extractor = csv_extractor.CsvCustomerExtractor(txt_file)

    with pytest.raises(ExtractionError):
        extractor.extract()


def test_extract_fails_if_file_is_not_file(tmp_path):
    not_a_file = tmp_path

    extractor = csv_extractor.CsvCustomerExtractor(not_a_file)

    with pytest.raises(ExtractionError):
        extractor.extract()
