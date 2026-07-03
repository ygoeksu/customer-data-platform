from dataclasses import dataclass


@dataclass
class CleanCustomer:
    customer_id: int
    name: str
    email: str
    country: str
