from customer_data_platform.models.raw_customer import RawCustomer

import re

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")

VALID_COUNTRIES = {
    "Germany",
    "France",
    "Spain",
    "Italy",
    "United Kingdom",
}


class Validator:
    def validate_email(self, email: str) -> bool:
        return bool(EMAIL_PATTERN.fullmatch(email))

    def validate_name(self, name: str) -> bool:
        if not name:
            return False

        if not name.strip():
            return False

        return len(name.strip()) >= 2

    def validate_customer_id(self, customer_id: str) -> bool:
        return customer_id.isdigit()

    def validate_country(self, country: str) -> bool:
        return country in VALID_COUNTRIES

    def validate(self, customer: RawCustomer) -> list[str]:
        errors = list()
        if not self.validate_email(customer.email):
            errors.append("Email not valid")
        if not self.validate_name(customer.name):
            errors.append("Name not valid")
        if not self.validate_customer_id(customer.customer_id):
            errors.append("Customer id not valid")
        if not self.validate_country(customer.country):
            errors.append("Country not valid")
        return errors
