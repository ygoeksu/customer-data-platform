# Customer Data Platform

A production-style Python ETL platform that ingests customer data from CSV files, validates and transforms records, and loads them into a SQLite database. Built to demonstrate clean architecture, the repository pattern, dependency injection, type safety, and modern Python tooling.

---

## Architecture

The pipeline follows a strict Extract → Validate → Transform → Load flow:

```
data/customers.csv
        │
        ▼
  CsvCustomerExtractor        extract/
        │
        ▼
     Validator                validate/       ← rejects invalid records
        │
        ▼
    Transformer               transform/      ← normalizes names, emails
        │
        ▼
SQLiteCustomerRepository      load/           ← persists to SQLite
```

Business logic never touches storage directly — it only knows the `CustomerRepository` protocol. Swapping SQLite for PostgreSQL means writing one new class, nothing else.

---

## Project Structure

```
src/customer_data_platform/
├── extract/
│   ├── csv_extractor.py        # reads CSV, maps columns to RawCustomer
│   ├── protocols.py            # Extractor protocol
│   └── schema/
│       └── customer.py         # column name mapping config
├── validate/
│   └── validator.py            # validates RawCustomer, returns errors
├── transform/
│   └── transformer.py          # converts RawCustomer → CleanCustomer
├── load/
│   ├── database.py             # SQLAlchemy engine setup
│   ├── init_db.py              # schema creation
│   └── repositories/
│       ├── customer_repository.py          # Repository protocol
│       └── sqlite_customer_repository.py   # SQLite implementation
├── models/
│   ├── raw_customer.py         # unvalidated input model
│   └── clean_customer.py       # validated, normalized model
└── exceptions/
    ├── extraction.py
    └── validation.py

tests/
├── unit/
│   ├── extract/
│   ├── validate/
│   └── transform/
└── integration/
    ├── test_pipeline.py
    └── test_sqlite_customer_repository.py
```

---

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) — package manager
- Docker (optional, for containerized runs)

---

## Setup

```bash
# Install dependencies
uv sync
```

---

## Running the Pipeline

```bash
# Run directly
uv run python main.py
```

The pipeline reads from `data/customers-100000.csv` and loads valid records into `customers.db`.

### Run with Docker

```bash
# Build the image
docker build -t customer-data-platform .

# Run (mount the data directory so the container can read the CSV)
docker run --rm -v ./data:/app/data customer-data-platform
```

---

## Testing

```bash
# Run all tests with coverage
uv run pytest

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/
```

Coverage must stay above 90% (enforced in `pyproject.toml`).

---

## Code Quality

```bash
# Format
uv run black src/ tests/

# Lint
uv run ruff check src/ tests/

# Type check
uv run mypy src/
```

---

## Documentation

Reference docs are in `docs/`:

| File | Topic |
|---|---|
| `en_python-fundamentals.md` / `de_python-grundlagen.md` | How Python executes code, decorators |
| `en_python-type-system.md` / `de_python-typsystem.md` | Type annotations, dataclasses, Pydantic, Protocols |
| `en_design-patterns.md` / `de_design-patterns.md` | Repository pattern |
| `en_testing-and-quality.md` / `de_testing-und-qualitaet.md` | pytest, fixtures, coverage, black, ruff, mypy |
| `en_databases.md` / `de_datenbanken.md` | SQLite |
| `en_docker.md` / `de_docker.md` | Docker, image registries, ETL patterns |
