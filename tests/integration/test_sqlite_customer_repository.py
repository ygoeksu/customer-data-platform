# ☐ save() persists a customer
# ☐ get_by_id() returns the customer
# ☐ get_by_id() returns None for missing customer
# ☐ get_all() returns all customers
# ☐ get_all() returns [] for an empty database
# ☐ Duplicate customer_id behavior (replace or reject)
# ☐ Unicode round-trip
import sqlite3
import pytest

from customer_data_platform.load.init_db import init_db
from customer_data_platform.load.repositories.sqlite_customer_repository import (
    SQLiteCustomerRepository,
)
from customer_data_platform.models.clean_customer import CleanCustomer


@pytest.fixture
def repository(tmp_path):
    db_path = tmp_path / "test.db"

    init_db(db_path)

    return SQLiteCustomerRepository(db_path)


def test_save_persists_customer(repository):
    # Arrange
    customer = CleanCustomer(
        customer_id=1,
        name="John Doe",
        email="john@abc.de",
        country="Germany",
    )

    # Act
    repository.save(customer)

    # Assert
    saved = repository.get_by_id(1)

    print(saved)
    print(customer)
    assert saved == customer
