# Testing and Code Quality

Topics: pytest, fixtures, coverage, and the quality tools (black, ruff, mypy) used in this project.

---

## Tool Overview

| Tool | What it checks | Speed | When to run |
|---|---|---|---|
| **black** | Formatting | Very fast | Before commit / on save |
| **ruff** | Linting (bugs, bad patterns) | Very fast | Before commit / CI |
| **pytest** | Correctness | Medium | Local + CI |
| **coverage** | Test completeness | Medium | CI / PR checks |
| **mypy** | Type safety | Slower | CI or pre-commit |

---

## pytest

pytest is the standard Python testing framework. Tests are plain functions that start with `test_`:

```python
def test_addition():
    assert 1 + 1 == 2
```

### Running tests

```bash
pytest                        # run all tests
pytest tests/unit/            # run a specific directory
pytest -v                     # verbose output
pytest -k "test_customer"     # run tests matching a keyword
pytest --tb=short             # shorter tracebacks
```

### Assertions

pytest rewrites `assert` statements to produce helpful failure messages:

```python
def test_customer_name():
    customer = Customer(name="Alice")
    assert customer.name == "Bob"
# AssertionError: assert 'Alice' == 'Bob'
```

### Parametrize

Run the same test with multiple inputs:

```python
import pytest

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert a + b == expected
```

---

## Fixtures

[Fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html) provide reusable setup (and optional teardown) for tests. They keep tests independent and avoid repeating setup code.

### Defining a fixture

```python
import pytest

@pytest.fixture
def sample_customer():
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

### Using a fixture

Declare it as a parameter — pytest injects it automatically:

```python
def test_customer_name(sample_customer):
    assert sample_customer["name"] == "Alice"
```

### Teardown with `yield`

Run cleanup code after the test using `yield`:

```python
@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    yield conn          # test runs here
    conn.close()        # cleanup after test
```

### Fixture scope

Controls how long a fixture instance lives:

| Scope | Lifetime | When to use |
|---|---|---|
| `function` (default) | Each test | Most fixtures |
| `class` | Each test class | Shared class setup |
| `module` | Each test file | Expensive per-file setup |
| `session` | Entire test run | Database connections, heavy resources |

```python
@pytest.fixture(scope="session")
def database():
    db = create_database()
    yield db
    db.teardown()
```

### `conftest.py`

Fixtures defined in `conftest.py` are automatically available to all tests in the same directory and subdirectories — no import needed. This is the standard way to share fixtures across multiple test files.

```
tests/
  conftest.py          ← fixtures here are available to all tests below
  unit/
    test_customer.py
  integration/
    test_repository.py
```

You can override a fixture from `conftest.py` by redefining it with the same name in a subdirectory's `conftest.py`.

### Autouse

A fixture with `autouse=True` runs for every test in scope without being explicitly requested:

```python
@pytest.fixture(autouse=True)
def reset_state():
    yield
    cleanup_global_state()
```

---

## Coverage

[coverage.py](https://coverage.readthedocs.io/) tracks which lines of your code were actually executed during tests. It tells you which parts of the code your tests never reach.

### Installation

```bash
pip install coverage
```

### Running with pytest

```bash
coverage run -m pytest
coverage run -m pytest --source=src   # limit to src/ directory
```

### Reports

```bash
coverage report -m          # terminal summary with missed line numbers
coverage html               # annotated HTML in htmlcov/
```

Example terminal output:

```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/customer/repository.py     45      9    80%   23-25, 41, 55-60
```

### What the percentage means

80% coverage means roughly 1 in 5 statements was never reached by your tests. Higher is generally better, but 100% coverage does not guarantee correctness — it only means each line ran at least once.

### With pytest-cov (recommended shortcut)

```bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

---

## black — Formatter

black enforces a single, opinionated code style. It reformats your code automatically and produces no warnings — it just changes the file.

```bash
black src/ tests/           # format in-place
black --check src/ tests/   # check without changing (for CI)
```

black eliminates all style debates: line length, quote style, trailing commas. Configure it in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
```

---

## ruff — Linter

ruff is an extremely fast Python linter that replaces flake8, isort, and many plugins. It catches bugs and bad patterns:

```bash
ruff check src/ tests/        # report issues
ruff check --fix src/ tests/  # auto-fix what it can
```

Configure in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]   # pycodestyle, pyflakes, isort
```

---

## mypy — Static Type Checker

mypy checks type annotations statically without running the code:

```bash
mypy src/
```

It catches errors like passing the wrong type, calling methods that don't exist on a type, and returning the wrong type. It's slower than ruff but catches a different class of bugs.

Configure in `pyproject.toml`:

```toml
[tool.mypy]
strict = true
```

`strict = true` enables the most thorough checking, including requiring annotations on all functions.
