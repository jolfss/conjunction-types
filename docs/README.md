# Product/Intersection Types for Python

A complete implementation of Product (Intersection) types for Python 3.14+, providing mathematically elegant type containers with compile-time type safety and runtime flexibility.

## Overview

A `Product[T | S | ...]` is a container with an unordered set of types, containing exactly one instance of each type. This implementation provides a product type in the sense that the subclassing relation holds: `Product[T|...] <: T`.

Key features:
- **Permutation invariance**: Order doesn't matter
- **Type flattening**: Nested products are automatically flattened
- **Type safety**: Each type appears at most once
- **Composable**: Combine types with `&` operator
- **Flexible access**: Get individual values or create subsets

## Installation

This module requires Python 3.14+ with `typing_extensions` for PEP 747 support:

```bash
pip install typing_extensions --break-system-packages
```

## Type Hints and IDE Support

**This implementation includes complete type hints matching the original specification.** All classes, methods, and functions are fully annotated with PEP 695 (generic type parameters) and PEP 747 (TypeForm) syntax.

Type hints enable:
- Full IDE autocomplete and IntelliSense
- Static type checking with mypy/pyright
- Jump to definition and refactoring support
- Hover documentation in IDEs

See [TYPE_HINTS_REFERENCE.md](TYPE_HINTS_REFERENCE.md) for complete type annotation details.

Example with type hints:
```python
# Type-annotated Product type
IntStrFloat: ProductMeta[int | str | float] = Product[int | str | float]

# Type-annotated instance
my_product: Product[int | str | float] = Product(42, "hello", 3.14)

# Type-safe access
int_value: int = my_product[int]  # IDE knows this returns int
subset: Product[int | str] = my_product[int | str]  # IDE knows this returns Product
```

## Quick Start

```python
from product_types import Product

# Create a Product with basic types
isf = Product(5, "hello", 0.2)  # Product[int | str | float]

# Access values by type
print(isf[int])    # 5
print(isf[str])    # "hello"
print(isf[float])  # 0.2

# Modify values
isf[str] = "world"

# Get subset of types
int_str = isf[int | str]  # Product[int | str] containing (5, "world")
```

## Core Concepts

### 1. Permutation Invariance

Order of arguments doesn't matter:

```python
isf = Product(5, "hello", 0.2)
sfi = Product("hello", 0.2, 5)

assert isf == sfi  # True - order doesn't matter
assert type(isf) == type(sfi)  # Same type
```

### 2. Type Constructors

Define Product types explicitly:

```python
# Create a Product type
IntStrFloat = Product[int | str | float]

# Instantiate it
isf = IntStrFloat(5, "hello", 0.2)

# Or use named classes
class IntStringFloat(Product[int | str | float]):
    pass

isf = IntStringFloat(5, "hello", 0.2)
```

### 3. Type Division

Extract subsets of types:

```python
IntStrFloat = Product[int | str | float]

# Get a subset - "divide" the type
IntClass = IntStrFloat[int]           # Product[int]
StrFloatClass = IntStrFloat[str | float]  # Product[str | float]

# Check containment
assert int in IntClass              # True
assert str in IntClass              # False
```

### 4. Runtime Type Access

Access multiple types at once:

```python
isf = Product(5, "hello", 0.2)

# Get a subset at runtime
int_str = isf[int | str]  # Returns Product[int | str] with values (5, "hello")

print(int_str[int])  # 5
print(int_str[str])  # "hello"
```

### 5. Type Extension

Extend Product types with new types:

```python
IntStrFloat = Product[int | str | float]

# Add bool to the type
IntStrFloatBool = Product[IntStrFloat | bool]
# Equivalent to: Product[int | str | float | bool]

assert int in IntStrFloatBool   # True
assert bool in IntStrFloatBool  # True
```

### 6. Type Composition with &

Combine Product types using the `&` operator:

```python
# Combine type constructors
IntStr = Product[int] & Product[str]  # Product[int | str]
IntStrFloat = IntStr & Product[float]  # Product[int | str | float]

# Combine instances
isf = Product(5, "hello", 0.2)
b = Product(True)
isfb = isf & b  # Product[int | str | float | bool]
```

### 7. Updating Values with `with_changes`

Create modified copies with left-to-right evaluation:

```python
isf = Product(5, "hello", 0.2)
is_update = Product(6, "world")
b_update = Product(True)

# Apply updates left-to-right
isfb = isf.with_changes(is_update, b_update)
# Result: Product[int | str | float | bool] with values (6, "world", 0.2, True)

# Later values override earlier ones
isfb2 = isf.with_changes(b_update, Product(False))
# Result: Product[int | str | float | bool] with bool=False
```

### 8. Type Flattening

Nested products are automatically flattened:

```python
T1 = Product[int | str | float]
T2 = Product[Product[int | str] | float]
T3 = Product[int | Product[Product[float] | str]]

assert T1 == T2 == T3  # All equivalent due to flattening
```

This ensures a canonical form for any set of types, which is crucial for type comparison and subclassing.

### 9. Type Containment

Check if types or Product types are contained in another:

```python
IntStr = Product[int | str]
IntStrFloat = Product[int | str | float]

# Single type containment
assert int in IntStr              # True
assert float in IntStr            # False

# Product type containment
assert IntStr in IntStrFloat      # True (subset)
assert IntStrFloat in IntStr      # False (not a subset)
```

## Design Decisions

### Why Flatten Nested Products?

Flattening ensures that there's a unique canonical form for any set of types. This means:
- Type equality is unambiguous
- Subclassing relationships are clear
- No confusion about "levels" of products

Without flattening, `Product[Product[int] | str]` and `Product[int | str]` would be different types, which would be confusing and break mathematical properties.

### Why Use `|` for Products?

While it may seem ironic to use the union operator for product types, this choice:
1. Avoids issues with `TypeVarTuple`
2. Enforces type-order invariance
3. Ensures non-duplicity
4. Provides type resolution over type constructor operations
5. Stays syntactically elegant

The `&` operator is available for combining Product types that have already been lifted into the Product type system.

### Distribution Over Sum

Product types distribute over sum types: within a `Product[...]`, the `|` operator functions like `&`. This is why `Product[int | str]` is equivalent to `Product[int] & Product[str]`.

## API Reference

### `Product` Class

#### Instance Creation

```python
Product(*args)
```

Create a Product instance with the given values. Each value is stored by its type.

#### Instance Methods

- `__getitem__(self, key)`: Get value(s) by type
  - Single type: returns the value
  - Multiple types: returns a new Product with those types
  
- `__setitem__(self, key, value)`: Set a value by type

- `with_changes(self, *args)`: Create a new Product with updated values (left-to-right)

- `__and__(self, other)`: Combine with another Product or value

- `__eq__(self, other)`: Check equality (permutation invariant)

### `ProductMeta` Metaclass

#### Type Methods

- `__getitem__(cls, types)`: Type division - create subset Product type

- `__and__(cls, other)`: Combine two Product types

- `__contains__(cls, item)`: Check if type(s) are in this Product type

- `__eq__(cls, other)`: Check type equality

### Helper Functions

#### `make_product_type(*types)`

Create a Product type from a list of types:

```python
IntStrFloat = make_product_type(int, str, float)
isf = IntStrFloat(1, "hello", 3.14)
```

## Complete Example

```python
from product_types import Product

# Define types
class IntStringFloat(Product[int | str | float]):
    pass

class BoolClass(Product[bool]):
    pass

# Create instances
isf = IntStringFloat(5, "hello", 0.2)
is_update = Product(6, "world")
b = BoolClass(True)

# Combine and update
isfb = isf.with_changes(is_update, b, BoolClass(False))
# Result: IntStringFloatBool(6, "world", 0.2, False)

# Access values
print(isfb[int])     # 6
print(isfb[str])     # "world"
print(isfb[float])   # 0.2
print(isfb[bool])    # False

# Get subsets
int_str = isfb[int | str]  # Product[int | str]

# Type operations
IntClass = IntStringFloat[str]  # Type division
StrFloatClass = IntStringFloat[str | float]

# Check containment
assert int in IntStringFloat
assert Product[str | int] in isfb.__class__

# Combine types
Combined = Product[int] & Product[str] & Product[float] & Product[bool]
assert Combined == type(isfb)
```

## Comparison with Other Approaches

### vs. dataclass

```python
# Traditional dataclass with multiple inheritance issues
@dataclass
class IntString:
    i: int
    s: str

@dataclass
class StringFloat:
    s: str
    f: float

# Multiple inheritance doesn't work well
# class IntStringFloat(IntString, StringFloat):  # Problems!

# Product types handle this elegantly
IntStringFloat = Product[int | str | float]
```

### vs. TypedDict

```python
# TypedDict requires string keys
from typing import TypedDict

class Data(TypedDict):
    i: int
    s: str
    f: float

# Must use string keys - not type-safe
data = Data(i=5, s="hello", f=0.2)

# Product types use actual types as keys
isf = Product(5, "hello", 0.2)
print(isf[int])  # Type-safe access
```

## Testing

Run the comprehensive test suite:

```bash
python test_product_types.py
```

This tests all features:
- Basic creation and access
- Permutation invariance
- Type constructors
- Type division
- Runtime type access
- Type extension
- & operator (type and instance)
- with_changes method
- Type equivalence and flattening
- Type containment
- Named classes

## Future Directions

When native Product types are added to Python, we'll be able to replace:
```python
Product[int | str | float]
```

with:
```python
int & str & float
```

Until then, this implementation provides full Product type functionality with minimal syntax overhead.

## License

This implementation is provided as-is for educational and practical use in Python 3.14+ projects.

## Contributing

This is a reference implementation of PEP 747-compatible Product types. Contributions, bug reports, and suggestions are welcome.
