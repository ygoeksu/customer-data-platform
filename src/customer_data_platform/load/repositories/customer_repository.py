from typing import Protocol
from customer_data_platform.models.clean_customer import CleanCustomer


class CustomerRepository(Protocol):

    def save(self, customer: CleanCustomer) -> None: ...

    def get_by_id(self, customer_id: int) -> CleanCustomer | None: ...
