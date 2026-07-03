import csv

from customer_data_platform.models.raw_customer import RawCustomer
from customer_data_platform.exceptions.extraction import ExtractionError
from customer_data_platform.extract.schema.customer import CsvCustomerSchema
from pathlib import Path


class CsvCustomerExtractor:
    def __init__(self, file_path: str, schema: CsvCustomerSchema | None = None) -> None:
        self.file_path = file_path
        self.schema = schema or CsvCustomerSchema()

    def extract(self) -> list[RawCustomer]:
        customers: list[RawCustomer] = []

        validate_file(Path(self.file_path))

        with open(self.file_path, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            missing_columns = [
                col
                for col in self.schema.required_columns()
                if col not in reader.fieldnames
            ]

            if missing_columns:
                raise ExtractionError(f"Missing columns: {missing_columns}")

            for row in reader:
                customers.append(
                    RawCustomer(
                        customer_id=row[self.schema.customer_id],
                        name=row[self.schema.name],
                        email=row[self.schema.email],
                        country=row[self.schema.country],
                    )
                )

        return customers


def validate_file(path: Path) -> None:
    if not path.exists():
        raise ExtractionError(path)

    if not path.is_file():
        raise ExtractionError("Not a file")

    if path.suffix != ".csv":
        raise ExtractionError("Not a CSV")

    if path.stat().st_size == 0:
        raise ExtractionError("File is empty")
