# Datenbanken

Themen: SQLite — was es ist, wie es funktioniert und wie man es aus Python heraus verwendet.

---

## SQLite

[SQLite](https://sqlite.org/) ist eine C-Bibliothek, die eine vollständige SQL-Datenbank-Engine in einer einzigen Datei implementiert. Es ist die am weitesten verbreitete Datenbank der Welt — eingesetzt in mobilen Apps, Browsern, Betriebssystemen und unzähligen anderen Anwendungen.

### Hauptmerkmale

| Eigenschaft | SQLite |
|---|---|
| Speicherung | Eine einzige `.db`-Datei auf der Festplatte |
| Serverprozess | Keiner — läuft im Prozess |
| Installation | Keine — in Python eingebaut |
| Datengröße | Bis zu 281 TB |
| Nebenläufigkeit | Gut für Lesezugriffe; eingeschränkte gleichzeitige Schreibzugriffe |
| SQL-Standard | Vollständiges SQL mit einigen Erweiterungen |

### Wann SQLite verwenden

**Gut geeignet:**
- Lokale Anwendungsdaten und Caches
- Prototyping und Entwicklung
- Tests (`:memory:` für flüchtige Datenbanken verwenden)
- Einzelbenutzeranwendungen oder eingebettete Geräte
- Lesezugriff-intensive Workloads

**Nicht geeignet:**
- Workloads mit vielen gleichzeitigen Schreibzugriffen
- Multi-Server-Deployments (kein Netzwerkprotokoll)
- Sehr große Datensätze, die Partitionierung oder Replikation erfordern

Für Produktionssysteme mit mehreren gleichzeitigen Schreibern oder verteilter Infrastruktur stattdessen PostgreSQL oder MySQL verwenden.

---

## Pythons `sqlite3`-Modul

Python enthält `sqlite3` in seiner Standardbibliothek — keine Installation erforderlich.

### Verbindung zu einer Datenbank herstellen

```python
import sqlite3

# Persistente Datenbankdatei
conn = sqlite3.connect("customers.db")

# In-Memory-Datenbank (ideal für Tests — verschwindet, wenn die Verbindung geschlossen wird)
conn = sqlite3.connect(":memory:")
```

### Eine Tabelle erstellen

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

### Daten einfügen

Immer parametrisierte Abfragen (`?`-Platzhalter) verwenden — niemals Benutzereingaben direkt in SQL-Strings formatieren. Das verhindert SQL-Injection.

```python
# Sicher — parametrisiert
cursor.execute(
    "INSERT INTO customers (name, email, age) VALUES (?, ?, ?)",
    ("Alice", "alice@example.com", 30)
)
conn.commit()

# Mehrere Zeilen auf einmal
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

### Daten abfragen

```python
# Alle Zeilen abrufen
cursor.execute("SELECT * FROM customers")
rows = cursor.fetchall()  # Liste von Tupeln

# Eine Zeile abrufen
cursor.execute("SELECT * FROM customers WHERE id = ?", (1,))
row = cursor.fetchone()  # Tupel oder None

# Über Ergebnisse iterieren
cursor.execute("SELECT name, email FROM customers")
for name, email in cursor:
    print(name, email)
```

### Row factory — Dicts statt Tupeln erhalten

```python
conn.row_factory = sqlite3.Row  # Zeilen verhalten sich wie Dicts

cursor.execute("SELECT * FROM customers WHERE id = ?", (1,))
row = cursor.fetchone()
print(row["name"])   # Zugriff über Spaltenname
```

### Context Manager verwenden

`with conn:` verwenden, um bei Erfolg automatisch zu committen und bei Ausnahmen zurückzurollen:

```python
with sqlite3.connect("customers.db") as conn:
    conn.execute(
        "UPDATE customers SET age = ? WHERE id = ?",
        (31, 1)
    )
# conn.commit() wird beim Verlassen automatisch aufgerufen
```

### Verbindung schließen

```python
conn.close()
```

Oder `with sqlite3.connect(...) as conn:` verwenden — beachte dabei, dass `with` nur Commit/Rollback behandelt, nicht das Schließen. Für explizites Aufräumen `try/finally` oder einen Context-Manager-Wrapper verwenden.

---

## SQLite in Tests

In Tests `:memory:`-Datenbanken verwenden, um für jeden Test eine frische, isolierte Datenbank zu erhalten, ohne das Dateisystem zu berühren:

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

Jeder Test bekommt seine eigene leere Datenbank — kein Zustandsleck zwischen Tests.
