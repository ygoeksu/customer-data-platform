# Python Fundamentals

Topics: how Python executes code, and how decorators extend behavior without modifying it.

---

## Interpreted vs. Compiled Languages

Languages differ in how source code becomes running instructions.

| | Compiled | Interpreted |
|---|---|---|
| Translation step | Before execution (compiler) | At runtime (interpreter) |
| Speed | Faster | Slower |
| Error detection | Compile-time | Runtime |
| Examples | C, C++, Rust, Go | JavaScript, Ruby, Perl |

### Where Python fits

Python is classified as **interpreted**, but it actually blends both approaches:

1. Python compiles your `.py` source file to **bytecode** (`.pyc` files in `__pycache__/`)
2. The **Python Virtual Machine (PVM)** then interprets that bytecode at runtime

This means Python gets some compilation benefits (syntax errors caught early, reusable bytecode) while retaining interpreted flexibility:

- Code can be modified and re-run without a separate build step
- Objects and modules can be inspected at runtime
- Errors in code paths that aren't executed don't surface until those paths run

### Practical impact

inc0564654

```bash
# No separate build step needed — just run:
python main.py
```

The interpreter handles everything. This is why Python is fast to iterate with but slower to execute than fully compiled languages like C or Go.

---

## Decorators

Decorators are functions (or callable objects) that **modify or extend the behavior of another function, method, or class without changing its source code**.

The `@decorator` syntax is shorthand:

```python
@decorator
def greet():
    print("Hello, World!")

# Exactly equivalent to:
def greet():
    print("Hello, World!")
greet = decorator(greet)
```

### How they work

Three Python features enable decorators:

- **First-class functions** — functions can be passed as arguments and returned from functions
- **Higher-order functions** — functions that accept or return other functions
- **Closures** — the inner `wrapper` retains access to the outer `func` variable

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        print("Before the function runs.")
        result = func(*args, **kwargs)
        print("After the function runs.")
        return result
    return wrapper

@decorator
def greet(name: str) -> None:
    print(f"Hello, {name}!")

greet("Alice")
# Before the function runs.
# Hello, Alice!
# After the function runs.
```

### Preserving metadata with `functools.wraps`

Wrapping a function hides its original `__name__` and `__doc__`. Fix this with `@wraps`:

```python
from functools import wraps

def decorator(func):
    @wraps(func)  # copies name, docstring, and other metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

### Stacking decorators

Decorators apply **bottom-up** — the one closest to the function applies first:

```python
@A
@B
def foo(): ...

# Equivalent to: foo = A(B(foo))
# B wraps foo first, then A wraps the result.
```

### Built-in decorators

Python provides three class-level decorators out of the box:

#### `@staticmethod`

A method that belongs to the class namespace but receives neither `self` nor `cls`. Use it for utility functions logically grouped with the class.

```python
class MathUtils:
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b

MathUtils.add(2, 3)  # callable without an instance
```

#### `@classmethod`

Receives the **class** (`cls`) as its first argument instead of the instance. Used for alternative constructors or class-level operations.

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

Lets you expose a method **as if it were an attribute**, enabling encapsulation with optional setter/deleter logic.

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
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self) -> float:
        import math
        return math.pi * self._radius ** 2

c = Circle(5.0)
print(c.area)    # accessed like an attribute, not c.area()
c.radius = 10.0  # calls the setter
```
