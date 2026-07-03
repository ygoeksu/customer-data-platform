# Python-Grundlagen

Themen: wie Python Code ausführt und wie Dekoratoren Verhalten erweitern, ohne es zu verändern.

---

## Interpretierte vs. kompilierte Sprachen

Sprachen unterscheiden sich darin, wie Quellcode zu ausführbaren Anweisungen wird.

| | Kompiliert | Interpretiert |
|---|---|---|
| Übersetzungsschritt | Vor der Ausführung (Compiler) | Zur Laufzeit (Interpreter) |
| Geschwindigkeit | Schneller | Langsamer |
| Fehlererkennung | Compilezeit | Laufzeit |
| Beispiele | C, C++, Rust, Go | JavaScript, Ruby, Perl |

### Wo Python einzuordnen ist

Python gilt als **interpretiert**, kombiniert aber beide Ansätze:

1. Python kompiliert `.py`-Quelldateien zu **Bytecode** (`.pyc`-Dateien in `__pycache__/`)
2. Die **Python Virtual Machine (PVM)** interpretiert diesen Bytecode dann zur Laufzeit

Python profitiert damit von einigen Vorteilen kompilierter Sprachen (Syntaxfehler werden früh erkannt, Bytecode ist wiederverwendbar) und behält gleichzeitig die Flexibilität interpretierter Sprachen:

- Code kann verändert und erneut ausgeführt werden, ohne einen separaten Build-Schritt
- Objekte und Module können zur Laufzeit inspiziert werden
- Fehler in nicht ausgeführten Codepfaden tauchen erst auf, wenn diese Pfade durchlaufen werden

### Praktische Auswirkung

```bash
# Kein separater Build-Schritt nötig — einfach ausführen:
python main.py
```

Der Interpreter übernimmt alles. Deshalb ist Python schnell in der Entwicklung, aber langsamer in der Ausführung als vollständig kompilierte Sprachen wie C oder Go.

---

## Dekoratoren

Dekoratoren sind Funktionen (oder aufrufbare Objekte), die das **Verhalten einer anderen Funktion, Methode oder Klasse erweitern oder verändern, ohne deren Quellcode zu ändern**.

Die `@Dekorator`-Syntax ist eine Abkürzung:

```python
@dekorator
def greet():
    print("Hallo, Welt!")

# Exakt gleichbedeutend mit:
def greet():
    print("Hallo, Welt!")
greet = dekorator(greet)
```

### Wie sie funktionieren

Drei Python-Features ermöglichen Dekoratoren:

- **First-class functions** — Funktionen können als Argumente übergeben und von Funktionen zurückgegeben werden
- **Higher-order functions** — Funktionen, die andere Funktionen akzeptieren oder zurückgeben
- **Closures** — die innere `wrapper`-Funktion behält Zugriff auf die äußere Variable `func`

```python
def dekorator(func):
    def wrapper(*args, **kwargs):
        print("Vor der Funktion.")
        result = func(*args, **kwargs)
        print("Nach der Funktion.")
        return result
    return wrapper

@dekorator
def greet(name: str) -> None:
    print(f"Hallo, {name}!")

greet("Alice")
# Vor der Funktion.
# Hallo, Alice!
# Nach der Funktion.
```

### Metadaten mit `functools.wraps` erhalten

Das Umhüllen einer Funktion verdeckt ihren ursprünglichen `__name__` und `__doc__`. Das lässt sich mit `@wraps` beheben:

```python
from functools import wraps

def dekorator(func):
    @wraps(func)  # kopiert Name, Docstring und andere Metadaten
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### Dekoratoren stapeln

Dekoratoren werden **von unten nach oben** angewendet — der der Funktion am nächsten liegende wird zuerst ausgeführt:

```python
@A
@B
def foo(): ...

# Gleichbedeutend mit: foo = A(B(foo))
# B umhüllt foo zuerst, dann umhüllt A das Ergebnis.
```

### Eingebaute Dekoratoren

Python stellt drei klassenbasierte Dekoratoren bereit:

#### `@staticmethod`

Eine Methode, die zum Klassen-Namespace gehört, aber weder `self` noch `cls` erhält. Verwende ihn für Hilfsfunktionen, die logisch zur Klasse gehören.

```python
class MathUtils:
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b

MathUtils.add(2, 3)  # aufrufbar ohne eine Instanz
```

#### `@classmethod`

Erhält die **Klasse** (`cls`) als erstes Argument anstelle der Instanz. Wird für alternative Konstruktoren oder klassenweite Operationen verwendet.

```python
class Customer:
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email

    @classmethod
    def from_dict(cls, data: dict) -> "Customer":
        return cls(name=data["name"], email=data["email"])

c = Customer.from_dict({"name": "Alice", "email": "alice@example.com"})
```

#### `@property`

Ermöglicht es, eine Methode **wie ein Attribut** anzusprechen, und bietet Kapselung mit optionaler Setter/Deleter-Logik.

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius darf nicht negativ sein")
        self._radius = value

    @property
    def area(self) -> float:
        import math
        return math.pi * self._radius ** 2

c = Circle(5.0)
print(c.area)    # wird wie ein Attribut aufgerufen, nicht c.area()
c.radius = 10.0  # ruft den Setter auf
```
