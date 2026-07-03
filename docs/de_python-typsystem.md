# Python-Typsystem

Themen: Typannotationen, Dataclasses, Pydantic, Protocols — die Werkzeuge, die Python zur Verfügung stellt, um Datenstrukturen auszudrücken und durchzusetzen.

---

## Typannotationen

Typannotationen sind Hinweise auf die erwarteten Typen von Variablen, Funktionsparametern und Rückgabewerten. Die Python-Laufzeit **erzwingt sie nicht** — sie existieren für statische Prüfwerkzeuge (mypy), IDEs und Leser.

```python
def greet(name: str) -> str:
    return f"Hallo, {name}"

x: int = 5
```

### Häufige Typen

| Annotation | Bedeutung |
|---|---|
| `str`, `int`, `float`, `bool` | Primitive Typen |
| `list[str]` | Liste von Strings (Python 3.9+) |
| `dict[str, int]` | Dict mit String-Schlüsseln und Int-Werten |
| `tuple[int, str]` | Tupel mit fester Länge |
| `int \| None` | Entweder int oder None (Python 3.10+) |
| `Optional[int]` | Gleichbedeutend mit `int \| None` (älterer Stil) |
| `Union[int, str]` | Einer von mehreren Typen |
| `Any` | Notausgang — keine Prüfung |
| `Callable[[int], bool]` | Eine Funktion, die int nimmt und bool zurückgibt |

### Rückgabetypen

```python
def log(msg: str) -> None: ...        # kein Rückgabewert
def crash() -> Never: raise ...       # gibt nie zurück
def count() -> Iterator[int]: ...     # Generator
```

### Typ-Aliase

```python
# Modern (Python 3.12+)
type Vector = list[float]

# Älterer Stil
from typing import TypeAlias
Vector: TypeAlias = list[float]
```

### Wie mypy Annotationen verwendet

mypy führt statische Analyse durch, ohne den Code auszuführen. Es meldet Typfehler, bevor das Programm jemals läuft:

```python
def double(x: int) -> int:
    return x * 2

double("hello")  # mypy-Fehler: int erwartet, str erhalten
```

Funktionen ohne Annotationen werden standardmäßig als `Any` behandelt — mypy überspringt sie. Annotationen schrittweise hinzuzufügen erhöht die Sicherheit zunehmend.

---

## Dataclasses

Dataclasses (eingeführt in Python 3.7, [PEP 557](https://docs.python.org/3/library/dataclasses.html)) generieren automatisch Boilerplate wie `__init__`, `__repr__` und `__eq__` aus Feldannotationen.

```python
from dataclasses import dataclass

@dataclass
class Customer:
    name: str
    email: str
    age: int = 0  # Standardwert
```

Der `@dataclass`-Dekorator generiert dieses `__init__` automatisch:

```python
def __init__(self, name: str, email: str, age: int = 0):
    self.name = name
    self.email = email
    self.age = age
```

### Wichtige Parameter

| Parameter | Standard | Effekt |
|---|---|---|
| `init` | `True` | `__init__` generieren |
| `repr` | `True` | `__repr__` generieren |
| `eq` | `True` | `__eq__` generieren |
| `order` | `False` | Vergleichsoperatoren generieren |
| `frozen` | `False` | Instanzen unveränderlich machen |
| `slots` | `False` | `__slots__` für Speichereffizienz verwenden |

### Veränderliche Standardwerte und `field()`

Veränderliche Standardwerte niemals direkt setzen — stattdessen `field(default_factory=...)` verwenden:

```python
from dataclasses import dataclass, field

@dataclass
class Order:
    items: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict, repr=False)
```

### Berechnete Felder mit `__post_init__`

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
```

### Frozen (unveränderliche) Dataclasses

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
p.x = 3.0  # löst FrozenInstanceError aus
```

### Hilfsfunktionen

```python
from dataclasses import asdict, astuple, replace, fields

asdict(customer)          # {'name': 'Alice', 'email': '...', 'age': 30}
astuple(customer)         # ('Alice', '...', 30)
replace(customer, age=31) # neue Instanz mit geändertem age
fields(customer)          # Tupel von Field-Deskriptoren
```

### Wann Dataclasses verwenden

- Data Transfer Objects (DTOs) zwischen Schichten
- Konfigurationsobjekte (mit `frozen=True`)
- Einfache Wertecontainer ohne Validierungslogik

---

## Pydantic

[Pydantic](https://docs.pydantic.dev/) fügt **Laufzeitvalidierung** auf Basis von Typannotationen hinzu. Während eine Dataclass Daten nur speichert, prüft und konvertiert ein Pydantic-Modell sie bei der Zuweisung.

```python
from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    age: int
    email: str

c = Customer(name="Sofia", age="30", email="sofia@example.com")
# age "30" (String) wird automatisch zu 30 (int) konvertiert
```

### Dataclass vs. Pydantic

| Feature | `@dataclass` | Pydantic `BaseModel` |
|---|---|---|
| Laufzeitvalidierung | Nein | Ja |
| Typkonvertierung | Nein | Ja (standardmäßig) |
| Eigene Validatoren | Manuell | `@field_validator` |
| JSON-Serialisierung | Via `asdict()` | `.model_dump()`, `.model_dump_json()` |
| Fehlerberichte | Nein | `ValidationError` mit Details |

### Validierungsfeatures

```python
from pydantic import BaseModel, field_validator, model_validator

class UserRegistration(BaseModel):
    username: str
    password: str
    confirm_password: str

    @field_validator("username")
    @classmethod
    def username_must_be_lowercase(cls, v: str) -> str:
        if v != v.lower():
            raise ValueError("Benutzername muss kleingeschrieben sein")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegistration":
        if self.password != self.confirm_password:
            raise ValueError("Passwörter stimmen nicht überein")
        return self
```

### Wann Pydantic verwenden

- Eingehende Daten validieren (API-Anfragen, Konfigurationsdateien, CSV-Importe)
- Überall dort, wo der Datenquelle nicht vertraut werden kann
- Wenn strukturierte `ValidationError`-Meldungen benötigt werden

Verwende einfache **Dataclasses** für interne Daten, die du kontrollierst; verwende **Pydantic** an Systemgrenzen (Benutzereingaben, externe APIs, Datei-Parsing).

---

## Protocols

[Protocols](https://typing.python.org/en/latest/spec/protocol.html) ermöglichen **strukturelles Subtyping** — eine Klasse erfüllt ein Protocol, wenn sie die richtigen Methoden und Attribute hat, unabhängig von Vererbung. Das ist Pythons formale Version von Duck Typing.

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...
```

Jede Klasse mit einer `close(self) -> None`-Methode erfüllt `Closeable` — ohne `class MyClass(Closeable)`.

### Protocol vs. ABC

| | ABC | Protocol |
|---|---|---|
| Subtyping | Nominal (muss erben) | Strukturell (muss Form entsprechen) |
| Explizite Registrierung | Erforderlich | Nicht erforderlich |
| Laufzeit-`isinstance`-Prüfung | Standard | Opt-in via `@runtime_checkable` |

### Ein Protocol definieren

```python
from typing import Protocol

class Repository(Protocol):
    def get_by_id(self, id: int) -> dict: ...
    def save(self, entity: dict) -> None: ...
```

Jede Klasse, die `get_by_id` und `save` mit passenden Signaturen implementiert, erfüllt `Repository` — ohne davon zu erben.

### Laufzeitprüfungen

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

isinstance(my_obj, Drawable)  # funktioniert nur mit @runtime_checkable
```

### Wann Protocols verwenden

- Interfaces definieren, ohne Aufrufer an eine bestimmte Implementierungsklasse zu binden
- Typsicheren Code schreiben, der trotzdem jedes Objekt mit der richtigen Form akzeptiert
- Bevorzugt gegenüber ABCs, wenn die geprüften Klassen nicht in eigenem Besitz sind (Drittanbieter-Typen)
