from customer_data_platform.models.raw_customer import RawCustomer
from customer_data_platform.validate.validator import Validator


def test_valid_customer(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="joe", email="joe@gmail.com", country="Germany"
    )

    expected_result = []
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_invalid_customer_id(tmp_path):
    customer = RawCustomer(
        customer_id="a1", name="joe", email="joe@gmail.com", country="Germany"
    )

    expected_result = ["Customer id not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_invalid_email(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="joe", email="joegmail.com", country="Germany"
    )

    expected_result = ["Email not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_name_too_short(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="j", email="joe@gmail.com", country="Germany"
    )

    expected_result = ["Name not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_multiple_invalid_fields(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="j", email="joegmail.com", country="Germany"
    )

    expected_result = ["Email not valid", "Name not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_name_not_only_whitespace(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="   ", email="joe@gmail.com", country="Germany"
    )
    print("joe".split())

    expected_result = ["Name not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_empty_name(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="", email="joe@gmail.com", country="Germany"
    )

    expected_result = ["Name not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result


def test_invalid_country(tmp_path):
    customer = RawCustomer(
        customer_id="1", name="joe", email="joe@gmail.com", country="Algeria"
    )

    expected_result = ["Country not valid"]
    validator = Validator()
    assert validator.validate(customer) == expected_result
