# Design Patterns

Themen: das Repository-Pattern — eine Abstraktionsschicht zwischen Geschäftslogik und Datenspeicherung.

---

## Repository-Pattern

Das [Repository-Pattern](https://www.geeksforgeeks.org/system-design/repository-design-pattern/) ist eine Abstraktionsschicht, die zwischen der Geschäftslogik und der Datenspeicherung liegt. Es bietet eine einheitliche Schnittstelle zum Lesen und Schreiben von Daten und verbirgt dabei die Details darüber, *wie* und *wo* diese Daten gespeichert werden.

Stell es dir wie einen Bibliothekar vor: Du fragst nach einem Buch nach Titel, und der Bibliothekar holt es — dir ist es egal, ob es in Regal A oder Regal B steht, in einem physischen Gebäude oder einem digitalen Archiv.

### Warum es verwenden

| Problem ohne das Pattern | Wie das Pattern hilft |
|---|---|
| Geschäftslogik ist an SQL gekoppelt | Datenbank austauschen, ohne Geschäftscode zu ändern |
| Schwer unit-testbar | Im Test ein Fake-In-Memory-Repository einschleusen |
| Datenzugriffslogik verteilt | Zentral an einem Ort pro Entität |
| Wechsel der Speichertechnologie erfordert breiten Refactor | Nur die Repository-Implementierung ändert sich |

### Aufbau

Das Pattern besteht typischerweise aus drei Teilen:

1. **Interface / Protocol** — definiert *welche* Operationen es gibt (get, save, delete…)
2. **Konkrete Implementierung** — führt die eigentliche Datenbankarbeit durch
3. **Verwender** — Geschäftslogik, die nur das Interface kennt

```
Geschäftslogik  →  CustomerRepository (Protocol)
                         ↑
          ┌──────────────┴──────────────┐
  SQLiteCustomerRepository    InMemoryCustomerRepository
  (Produktion)                (Tests)
```

### Python-Beispiel

**Schritt 1 — Interface als Protocol definieren:**

```python
from typing import Protocol

class CustomerRepository(Protocol):
    def get_by_id(self, customer_id: int) -> dict | None: ...
    def get_all(self) -> list[dict]: ...
    def save(self, customer: dict) -> None: ...
    def delete(self, customer_id: int) -> None: ...
```

**Schritt 2 — Konkrete Implementierung schreiben:**

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

**Schritt 3 — Geschäftslogik hängt nur vom Interface ab:**

```python
class CustomerService:
    def __init__(self, repo: CustomerRepository):
        self.repo = repo

    def get_customer(self, customer_id: int) -> dict:
        customer = self.repo.get_by_id(customer_id)
        if customer is None:
            raise ValueError(f"Kunde {customer_id} nicht gefunden")
        return customer
```

**In der Produktion:**

```python
repo = SQLiteCustomerRepository(db_path="customers.db")
service = CustomerService(repo)
```

**In Tests:**

```python
repo = InMemoryCustomerRepository()
service = CustomerService(repo)
```

Der `CustomerService`-Code ändert sich nie — nur welches Repository eingeschleust wird.

### Alternative: Abstract Base Class

Statt eines Protocols kann eine ABC verwendet werden, die die Implementierung zum Zeitpunkt der Klassendefinition erzwingt, nicht erst bei der Typprüfung:

```python
from abc import ABC, abstractmethod

class CustomerRepository(ABC):
    @abstractmethod
    def get_by_id(self, customer_id: int) -> dict | None: ...

    @abstractmethod
    def save(self, customer: dict) -> None: ...
```

Konkrete Klassen müssen davon erben und alle abstrakten Methoden implementieren, sonst wirft Python bei der Instanziierung einen `TypeError`. Verwende ABCs, wenn du eine Laufzeitgarantie möchtest; verwende Protocols, wenn du strukturelles Typing ohne erzwungene Vererbung bevorzugst.

### Einschränkung

Sehr unterschiedliche Datenquellen (z.B. eine relationale Datenbank und ein Objektspeicher) in ein gemeinsames Interface zu zwingen, riskiert den Verlust von Fähigkeiten, die für jedes System einzigartig sind. Halte die Abstraktion auf einem Niveau, auf dem das Interface für alle Implementierungen sinnvoll bleibt.
