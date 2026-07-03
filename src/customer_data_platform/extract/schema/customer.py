from dataclasses import dataclass


@dataclass(frozen=True)
class CsvCustomerSchema:
    customer_id: str = "customer_id"
    name: str = "name"
    email: str = "email"
    country: str = "country"

    def required_columns(self) -> list[str]:
        return [
            self.customer_id,
            self.name,
            self.email,
            self.country,
        ]
