from customer_data_platform.models.clean_customer import CleanCustomer
from customer_data_platform.models.raw_customer import RawCustomer


class Transformer:

    def transform(self, customer: RawCustomer) -> CleanCustomer:
        return CleanCustomer(
            customer_id=int(customer.customer_id),
            name=customer.name.strip().title(),
            email=customer.email.strip().lower(),
            country=customer.country.strip().title(),
        )
