from pathlib import Path

from customer_data_platform.load.database import get_connection
from customer_data_platform.models.clean_customer import CleanCustomer


class SQLiteCustomerRepository:

    def __init__(self, db_path: str | Path):
        self.db_path = db_path

    def save(self, customer: CleanCustomer) -> None:
        with get_connection(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO customers (customer_id, name, email, country)
                VALUES (?, ?, ?, ?)
            """,
                (
                    customer.customer_id,
                    customer.name,
                    customer.email,
                    customer.country,
                ),
            )

    def get_by_id(self, customer_id: int) -> CleanCustomer | None:
        with get_connection(self.db_path) as conn:
            row = conn.execute(
                "SELECT customer_id, name, email, country FROM customers WHERE customer_id=?",
                (customer_id,),
            ).fetchone()

        if not row:
            return None

        return CleanCustomer(*row)
