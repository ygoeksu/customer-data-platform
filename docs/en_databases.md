# Databases

Topics: SQLite — what it is, how it works, and how to use it from Python.

---

## SQLite

[SQLite](https://sqlite.org/) is a C library that implements a full SQL database engine in a single file. It is the most widely deployed database in the world — used in mobile apps, browsers, operating systems, and countless other applications.

### Key characteristics

| Property | SQLite |
|---|---|
| Storage | A single `.db` file on disk |
| Server process | None — runs in-process |
| Installation | None — built into Python |
| Data size | Up to 281 TB |
| Concurrency | Good for reads; limited concurrent writes |
| SQL standard | Full SQL with some extensions |

### When to use SQLite

**Good fit:**
- Local application data and caches
- Prototyping and development
- Testing (use `:memory:` for ephemeral databases)
- Single-user applications or embedded devices
- Read-heavy workloads

**Not a good fit:**
- High-concurrency write workloads (many writers at once)
- Multi-server deployments (no network protocol)
- Very large datasets requiring partitioning or replication

For production systems with multiple concurrent writers or distributed infrastructure, use PostgreSQL or MySQL instead.

---

## Python's `sqlite3` Module

Python ships with `sqlite3` in its standard library — no installation needed.

### Connecting to a database

```python
import sqlite3

# Persistent database file
conn = sqlite3.connect("customers.db")

# In-memory database (perfect for tests — disappears when connection closes)
conn = sqlite3.connect(":memory:")
```

### Creating a table

```python
conn = sqlite3.connect("customers.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id      INTEGER PRIMARY KEY AUTOINCREMENT,
        name    TEXT    NOT NULL,
        email   TEXT    NOT NULL UNIQUE,
        age     INTEGER
    )
""")
conn.commit()
```

### Inserting data

Always use parameterized queries (`?` placeholders) — never format user input into SQL strings directly. This prevents SQL injection.

```python
# Safe — parameterized
cursor.execute(
    "INSERT INTO customers (name, email, age) VALUES (?, ?, ?)",
    ("Alice", "alice@example.com", 30)
)
conn.commit()

# Multiple rows at once
customers = [
    ("Bob", "bob@example.com", 25),
    ("Carol", "carol@example.com", 35),
]
cursor.executemany(
    "INSERT INTO customers (name, email, age) VALUES (?, ?, ?)",
    customers
)
conn.commit()
```

### Querying data

```python
# Fetch all rows
cursor.execute("SELECT * FROM customers")
rows = cursor.fetchall()  # list of tuples

# Fetch one row
cursor.execute("SELECT * FROM customers WHERE id = ?", (1,))
row = cursor.fetchone()  # tuple or None

# Iterate over results
cursor.execute("SELECT name, email FROM customers")
for name, email in cursor:
    print(name, email)
```

### Row factory — get dicts instead of tuples

```python
conn.row_factory = sqlite3.Row  # rows behave like dicts

cursor.execute("SELECT * FROM customers WHERE id = ?", (1,))
row = cursor.fetchone()
print(row["name"])   # access by column name
```

### Using a context manager

Use `with conn:` to automatically commit on success and roll back on exceptions:

```python
with sqlite3.connect("customers.db") as conn:
    conn.execute(
        "UPDATE customers SET age = ? WHERE id = ?",
        (31, 1)
    )
# conn.commit() called automatically on exit
```

### Closing the connection

```python
conn.close()
```

Or use `with sqlite3.connect(...) as conn:` — though note that `with` only handles commit/rollback, not closing. For explicit cleanup, use `try/finally` or a context manager wrapper.

---

## SQLite in Tests

Use `:memory:` databases in tests to get a fresh, isolated database for every test without touching the filesystem:

```python
import pytest
import sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    yield conn
    conn.close()

def test_insert_customer(db):
    db.execute("INSERT INTO customers VALUES (1, 'Alice', 'alice@example.com')")
    db.commit()
    row = db.execute("SELECT name FROM customers WHERE id = 1").fetchone()
    assert row[0] == "Alice"
```

Each test gets its own empty database — no state leaks between tests.
