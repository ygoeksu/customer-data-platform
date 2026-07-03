from typing import Protocol

from customer_data_platform.models.customer import Customer


class Extractor(Protocol):

    def extract(self) -> list[Customer]:
        raise NotImplementedError
