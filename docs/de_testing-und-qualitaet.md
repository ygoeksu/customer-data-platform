# Testing und Codequalität

Themen: pytest, Fixtures, Coverage und die Qualitätswerkzeuge (black, ruff, mypy), die in diesem Projekt verwendet werden.

---

## Werkzeugübersicht

| Werkzeug | Was es prüft | Geschwindigkeit | Wann ausführen |
|---|---|---|---|
| **black** | Formatierung | Sehr schnell | Vor dem Commit / beim Speichern |
| **ruff** | Linting (Bugs, schlechte Muster) | Sehr schnell | Vor dem Commit / CI |
| **pytest** | Korrektheit | Mittel | Lokal + CI |
| **coverage** | Testvollständigkeit | Mittel | CI / PR-Checks |
| **mypy** | Typsicherheit | Langsamer | CI oder Pre-commit |

---

## pytest

pytest ist das Standard-Python-Testframework. Tests sind einfache Funktionen, die mit `test_` beginnen:

```python
def test_addition():
    assert 1 + 1 == 2
```

### Tests ausführen

```bash
pytest                        # alle Tests ausführen
pytest tests/unit/            # ein bestimmtes Verzeichnis ausführen
pytest -v                     # ausführliche Ausgabe
pytest -k "test_customer"     # Tests nach Stichwort filtern
pytest --tb=short             # kürzere Tracebacks
```

### Assertions

pytest schreibt `assert`-Anweisungen um und produziert hilfreiche Fehlermeldungen:

```python
def test_customer_name():
    customer = Customer(name="Alice")
    assert customer.name == "Bob"
# AssertionError: assert 'Alice' == 'Bob'
```

### Parametrize

Denselben Test mit mehreren Eingaben ausführen:

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

[Fixtures](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html) bieten wiederverwendbares Setup (und optionales Teardown) für Tests. Sie halten Tests unabhängig voneinander und vermeiden wiederholten Setup-Code.

### Eine Fixture definieren

```python
import pytest

@pytest.fixture
def sample_customer():
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}
```

### Eine Fixture verwenden

Als Parameter deklarieren — pytest injiziert sie automatisch:

```python
def test_customer_name(sample_customer):
    assert sample_customer["name"] == "Alice"
```

### Teardown mit `yield`

Aufräumcode nach dem Test mit `yield` ausführen:

```python
@pytest.fixture
def db_connection():
    conn = sqlite3.connect(":memory:")
    yield conn          # Test läuft hier
    conn.close()        # Aufräumen nach dem Test
```

### Fixture-Scope

Steuert, wie lange eine Fixture-Instanz lebt:

| Scope | Lebensdauer | Wann verwenden |
|---|---|---|
| `function` (Standard) | Jeder Test | Die meisten Fixtures |
| `class` | Jede Testklasse | Gemeinsames Klassen-Setup |
| `module` | Jede Testdatei | Teures Setup pro Datei |
| `session` | Gesamter Testlauf | Datenbankverbindungen, schwere Ressourcen |

```python
@pytest.fixture(scope="session")
def database():
    db = create_database()
    yield db
    db.teardown()
```

### `conftest.py`

Fixtures, die in `conftest.py` definiert sind, stehen automatisch allen Tests im selben Verzeichnis und in Unterverzeichnissen zur Verfügung — kein Import nötig. Das ist der Standardweg, um Fixtures über mehrere Testdateien zu teilen.

```
tests/
  conftest.py          ← Fixtures hier gelten für alle Tests darunter
  unit/
    test_customer.py
  integration/
    test_repository.py
```

Eine Fixture aus `conftest.py` kann überschrieben werden, indem sie in der `conftest.py` eines Unterverzeichnisses mit demselben Namen neu definiert wird.

### Autouse

Eine Fixture mit `autouse=True` läuft für jeden Test im Scope, ohne explizit angefordert zu werden:

```python
@pytest.fixture(autouse=True)
def reset_state():
    yield
    cleanup_global_state()
```

---

## Coverage

[coverage.py](https://coverage.readthedocs.io/) verfolgt, welche Zeilen deines Codes während der Tests tatsächlich ausgeführt wurden. Es zeigt dir, welche Teile des Codes deine Tests nie erreichen.

### Installation

```bash
pip install coverage
```

### Mit pytest ausführen

```bash
coverage run -m pytest
coverage run -m pytest --source=src   # auf src/-Verzeichnis beschränken
```

### Berichte

```bash
coverage report -m          # Terminal-Zusammenfassung mit fehlenden Zeilennummern
coverage html               # annotiertes HTML in htmlcov/
```

Beispiel-Terminalausgabe:

```
Name                        Stmts   Miss  Cover   Missing
---------------------------------------------------------
src/customer/repository.py     45      9    80%   23-25, 41, 55-60
```

### Was der Prozentsatz bedeutet

80% Coverage bedeutet grob, dass 1 von 5 Anweisungen von deinen Tests nie erreicht wurde. Höher ist grundsätzlich besser, aber 100% Coverage garantiert keine Korrektheit — es bedeutet nur, dass jede Zeile mindestens einmal ausgeführt wurde.

### Mit pytest-cov (empfohlene Abkürzung)

```bash
pip install pytest-cov
pytest --cov=src --cov-report=term-missing
```

---

## black — Formatter

black erzwingt einen einzigen, meinungsstarken Code-Stil. Es formatiert Code automatisch um und erzeugt keine Warnungen — es ändert einfach die Datei.

```bash
black src/ tests/           # direkt formatieren
black --check src/ tests/   # prüfen ohne zu ändern (für CI)
```

black eliminiert alle Stildebatten: Zeilenlänge, Anführungszeichenstil, abschließende Kommas. Konfigurieren in `pyproject.toml`:

```toml
[tool.black]
line-length = 88
```

---

## ruff — Linter

ruff ist ein extrem schneller Python-Linter, der flake8, isort und viele Plugins ersetzt. Er erkennt Bugs und schlechte Muster:

```bash
ruff check src/ tests/        # Probleme melden
ruff check --fix src/ tests/  # automatisch beheben, was möglich ist
```

Konfigurieren in `pyproject.toml`:

```toml
[tool.ruff]
line-length = 88
select = ["E", "F", "I"]   # pycodestyle, pyflakes, isort
```

---

## mypy — Statischer Typprüfer

mypy prüft Typannotationen statisch, ohne den Code auszuführen:

```bash
mypy src/
```

Es erkennt Fehler wie das Übergeben des falschen Typs, das Aufrufen von Methoden, die auf einem Typ nicht existieren, und das Zurückgeben des falschen Typs. Es ist langsamer als ruff, erkennt aber eine andere Klasse von Bugs.

Konfigurieren in `pyproject.toml`:

```toml
[tool.mypy]
strict = true
```

`strict = true` aktiviert die gründlichste Prüfung, einschließlich der Anforderung von Annotationen für alle Funktionen.
