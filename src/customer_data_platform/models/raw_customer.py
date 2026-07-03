from dataclasses import dataclass


@dataclass
class RawCustomer:
    customer_id: str
    email: str
    name: str
    country: str
