# Python Type System

Topics: type annotations, dataclasses, Pydantic, Protocols — the tools Python gives you to express and enforce data structure.

---

## Type Annotations

Type annotations are hints about the expected types of variables, function parameters, and return values. The Python runtime **does not enforce them** — they exist for static checkers (mypy), IDEs, and readers.

```python
def greet(name: str) -> str:
    return f"Hello, {name}"

x: int = 5
```

### Common Types

| Annotation | Meaning |
|---|---|
| `str`, `int`, `float`, `bool` | Primitives |
| `list[str]` | List of strings (Python 3.9+) |
| `dict[str, int]` | Dict from string keys to int values |
| `tuple[int, str]` | Fixed-length tuple |
| `int \| None` | Either int or None (Python 3.10+) |
| `Optional[int]` | Same as `int \| None` (older style) |
| `Union[int, str]` | One of several types |
| `Any` | Escape hatch — no checking at all |
| `Callable[[int], bool]` | A function taking int and returning bool |

### Return types

```python
def log(msg: str) -> None: ...        # no return value
def crash() -> Never: raise ...       # never returns
def count() -> Iterator[int]: ...     # generator
```

### Type aliases

```python
# Modern (Python 3.12+)
type Vector = list[float]

# Older style
from typing import TypeAlias
Vector: TypeAlias = list[float]
```

### How mypy uses annotations

mypy performs static analysis without running the code. It flags type mismatches before the program ever runs:

```python
def double(x: int) -> int:
    return x * 2

double("hello")  # mypy error: expected int, got str
```

Functions without annotations default to `Any` — mypy skips them. Add annotations progressively to get increasing safety.

---

## Dataclasses

Dataclasses (introduced in Python 3.7, [PEP 557](https://docs.python.org/3/library/dataclasses.html)) automatically generate boilerplate like `__init__`, `__repr__`, and `__eq__` from field annotations.

```python
from dataclasses import dataclass

@dataclass
class Customer:
    name: str
    email: str
    age: int = 0  # default value
```

The `@dataclass` decorator generates this `__init__` automatically:

```python
def __init__(self, name: str, email: str, age: int = 0):
    self.name = name
    self.email = email
    self.age = age
```

### Key parameters

| Parameter | Default | Effect |
|---|---|---|
| `init` | `True` | Generate `__init__` |
| `repr` | `True` | Generate `__repr__` |
| `eq` | `True` | Generate `__eq__` |
| `order` | `False` | Generate comparison operators |
| `frozen` | `False` | Make instances immutable |
| `slots` | `False` | Use `__slots__` for memory efficiency |

### Mutable defaults and `field()`

Never use mutable defaults directly — use `field(default_factory=...)` instead:

```python
from dataclasses import dataclass, field

@dataclass
class Order:
    items: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict, repr=False)
```

### Computed fields with `__post_init__`

```python
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False)

    def __post_init__(self):
        self.area = self.width * self.height
```

### Frozen (immutable) dataclasses

```python
@dataclass(frozen=True)
class Point:
    x: float
    y: float

p = Point(1.0, 2.0)
p.x = 3.0  # raises FrozenInstanceError
```

### Utility functions

```python
from dataclasses import asdict, astuple, replace, fields

asdict(customer)          # {'name': 'Alice', 'email': '...', 'age': 30}
astuple(customer)         # ('Alice', '...', 30)
replace(customer, age=31) # new instance with age changed
fields(customer)          # tuple of Field descriptors
```

### When to use dataclasses

- Data Transfer Objects (DTOs) between layers
- Configuration objects (use `frozen=True`)
- Simple value containers without validation logic

---

## Pydantic

[Pydantic](https://docs.pydantic.dev/) adds **runtime validation** on top of type annotations. Where a dataclass just stores data, a Pydantic model checks and coerces it on assignment.

```python
from pydantic import BaseModel

class Customer(BaseModel):
    name: str
    age: int
    email: str

c = Customer(name="Sofia", age="30", email="sofia@example.com")
# age "30" (string) is automatically coerced to 30 (int)
```

### Dataclass vs. Pydantic

| Feature | `@dataclass` | Pydantic `BaseModel` |
|---|---|---|
| Runtime validation | No | Yes |
| Type coercion | No | Yes (by default) |
| Custom validators | Manual | `@field_validator` |
| JSON serialization | Via `asdict()` | `.model_dump()`, `.model_dump_json()` |
| Error reporting | No | `ValidationError` with details |

### Validation features

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
            raise ValueError("username must be lowercase")
        return v

    @model_validator(mode="after")
    def passwords_match(self) -> "UserRegistration":
        if self.password != self.confirm_password:
            raise ValueError("passwords do not match")
        return self
```

### When to use Pydantic

- Validating incoming data (API requests, config files, CSV imports)
- Anywhere you cannot trust the data source
- When you need structured `ValidationError` messages

Use plain **dataclasses** for internal data that you control; use **Pydantic** at system boundaries (user input, external APIs, file parsing).

---

## Protocols

[Protocols](https://typing.python.org/en/latest/spec/protocol.html) enable **structural subtyping** — a class satisfies a protocol if it has the right methods and attributes, regardless of inheritance. This is Python's formal version of duck typing.

```python
from typing import Protocol

class Closeable(Protocol):
    def close(self) -> None: ...
```

Any class with a `close(self) -> None` method satisfies `Closeable` — no `class MyClass(Closeable)` needed.

### Protocol vs. ABC

| | ABC | Protocol |
|---|---|---|
| Subtyping | Nominal (must inherit) | Structural (must match shape) |
| Explicit registration | Required | Not required |
| Runtime `isinstance` check | Default | Opt-in via `@runtime_checkable` |

### Defining a Protocol

```python
from typing import Protocol

class Repository(Protocol):
    def get_by_id(self, id: int) -> dict: ...
    def save(self, entity: dict) -> None: ...
```

Any class implementing `get_by_id` and `save` with matching signatures satisfies `Repository` without inheriting from it.

### Runtime checks

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Drawable(Protocol):
    def draw(self) -> None: ...

isinstance(my_obj, Drawable)  # works only with @runtime_checkable
```

### When to use Protocols

- Define interfaces without tying callers to a specific implementation class
- Write type-safe code that still accepts any object with the right shape
- Preferred over ABCs when you don't own the classes being checked (third-party types)
