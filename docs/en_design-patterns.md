# Design Patterns

Topics: the Repository pattern — an abstraction layer between business logic and data storage.

---

## Repository Pattern

The [Repository pattern](https://www.geeksforgeeks.org/system-design/repository-design-pattern/) is an abstraction layer that sits between your business logic and your data storage. It presents a consistent interface for reading and writing data while hiding the details of *how* and *where* that data is stored.

Think of it like a librarian: you ask for a book by title, and the librarian fetches it — you don't care whether it's on shelf A or shelf B, in a physical building or a digital archive.

### Why use it

| Problem without it | How the pattern helps |
|---|---|
| Business logic coupled to SQL | Swap the database without touching business code |
| Hard to unit test | Inject a fake in-memory repository in tests |
| Data access logic scattered | Centralized in one place per entity |
| Changing storage technology requires wide refactor | Only the repository implementation changes |

### Structure

The pattern typically has three parts:

1. **Interface / Protocol** — defines *what* operations exist (get, save, delete…)
2. **Concrete implementation** — does the actual database work
3. **Consumer** — business logic that only knows about the interface

```
Business Logic  →  CustomerRepository (Protocol)
                         ↑
          ┌──────────────┴──────────────┐
  SQLiteCustomerRepository    InMemoryCustomerRepository
  (production)                (tests)
```

### Python example

**Step 1 — Define the interface as a Protocol:**

```python
from typing import Protocol

class CustomerRepository(Protocol):
    def get_by_id(self, customer_id: int) -> dict | None: ...
    def get_all(self) -> list[dict]: ...
    def save(self, customer: dict) -> None: ...
    def delete(self, customer_id: int) -> None: ...
```

**Step 2 — Write a concrete implementation:**

```python
class InMemoryCustomerRepository:
    def __init__(self):
        self._store: dict[int, dict] = {}

    def get_by_id(self, customer_id: int) -> dict | None:
        return self._store.get(customer_id)

    def get_all(self) -> list[dict]:
        return list(self._store.values())

    def save(self, customer: dict) -> None:
        self._store[customer["id"]] = customer

    def delete(self, customer_id: int) -> None:
        self._store.pop(customer_id, None)
```

**Step 3 — Business logic depends only on the interface:**

```python
class CustomerService:
    def __init__(self, repo: CustomerRepository):
        self.repo = repo

    def get_customer(self, customer_id: int) -> dict:
        customer = self.repo.get_by_id(customer_id)
        if customer is None:
            raise ValueError(f"Customer {customer_id} not found")
        return customer
```

**In production:**

```python
repo = SQLiteCustomerRepository(db_path="customers.db")
service = CustomerService(repo)
```

**In tests:**

```python
repo = InMemoryCustomerRepository()
service = CustomerService(repo)
```

The `CustomerService` code never changes — only which repository gets injected.

### Abstract Base Class alternative

Instead of a Protocol you can use an ABC, which enforces implementation at class definition time rather than at type-check time:

```python
from abc import ABC, abstractmethod

class CustomerRepository(ABC):
    @abstractmethod
    def get_by_id(self, customer_id: int) -> dict | None: ...

    @abstractmethod
    def save(self, customer: dict) -> None: ...
```

Concrete classes must inherit from it and implement all abstract methods, or Python raises a `TypeError` at instantiation. Use ABCs when you want a runtime guarantee; use Protocols when you want structural typing without enforced inheritance.

### Caveat

Forcing very different data sources (e.g., a relational database and an object store) into one shared interface risks losing capabilities unique to each system. Keep the abstraction at a level where the interface stays meaningful across all implementations.
