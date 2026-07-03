from customer_data_platform.models.raw_customer import RawCustomer
from customer_data_platform.models.clean_customer import CleanCustomer
from customer_data_platform.transform.transformer import Transformer


def test_valid_transform(tmp_path):
    input = RawCustomer(
        "1", name="John surname ", email=" JOE@GMAIL.DE ", country="Germany "
    )
    transformer = Transformer()
    expected_result = CleanCustomer(
        1, name="John Surname", email="joe@gmail.de", country="Germany"
    )
    assert transformer.transform(input) == expected_result
