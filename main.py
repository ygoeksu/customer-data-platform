from customer_data_platform.extract.csv_extractor import CsvCustomerExtractor
from customer_data_platform.extract.schema.customer import CsvCustomerSchema
from customer_data_platform.validate.validator import Validator
from customer_data_platform.transform.transformer import Transformer
from customer_data_platform.load.init_db import init_db
from customer_data_platform.load.repositories.sqlite_customer_repository import (
    SQLiteCustomerRepository,
)


def run_pipeline(file_path: str):
    init_db(db_path="data/customers1.db")
    schema = CsvCustomerSchema(
        customer_id="Index", name="First Name", email="Email", country="Country"
    )
    extractor = CsvCustomerExtractor(file_path, schema)
    validator = Validator()
    transformer = Transformer()
    repository = SQLiteCustomerRepository("data/customers1.db")

    raw_customers = extractor.extract()
    invalid_customers = []
    for customer in raw_customers:
        errors = validator.validate(customer)
        if not errors:
            clean_customer = transformer.transform(customer)
            repository.save(clean_customer)
        else:
            invalid_customers.append((customer, errors))


if __name__ == "__main__":
    run_pipeline("data/customers-100000.csv")
