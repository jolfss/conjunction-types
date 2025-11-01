# Product Types

[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Typed](https://img.shields.io/badge/typed-yes-brightgreen.svg)](https://github.com/python/mypy)

Product/Intersection types for Python with full type hint support and IDE integration.

## Overview

A `Product[T | S | ...]` is a container with an unordered set of types, containing exactly one instance of each type. This implementation provides product types with:

- **Permutation invariance**: Order doesn't matter
- **Type flattening**: Nested products are automatically flattened
- **Full type hints**: Complete IDE support with PEP 695 and PEP 747
- **Type safety**: Each type appears at most once
- **Composable**: Combine types with `&` operator

## Installation

```bash
pip install product-types
```

Requires Python 3.14+ with `typing_extensions`:

```bash
pip install typing-extensions>=4.12.0
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
int_str = isf[int | str]  # Product[int | str]
```

## Type Hints

Full type hint support with IDE autocomplete:

```python
from product_types import Product, ProductMeta

# Type-annotated Product type
IntStrFloat: ProductMeta[int | str | float] = Product[int | str | float]

# Type-annotated instance
my_product: Product[int | str | float] = IntStrFloat(42, "hello", 3.14)

# Type-safe access
int_value: int = my_product[int]  # IDE knows this returns int
```

## Key Features

### Permutation Invariance

```python
p1 = Product(1, "hello", 3.14)
p2 = Product("hello", 3.14, 1)
assert p1 == p2  # True - order doesn't matter
```

### Type Constructors

```python
# Define a Product type
IntStrFloat = Product[int | str | float]

# Create instances
isf = IntStrFloat(42, "answer", 2.71)
```

### Type Division

```python
# Extract subsets
IntStrFloat = Product[int | str | float]
IntOnly = IntStrFloat[int]           # Product[int]
NumericTypes = IntStrFloat[int | float]  # Product[int | float]
```

### Type Composition

```python
# Combine types with &
Combined = Product[int] & Product[str] & Product[float]
# Result: Product[int | str | float]
```

### Runtime Type Access

```python
data = Product(42, "hello", 3.14, True)
nums = data[int | float]  # Get subset at runtime
```

### Functional Updates

```python
original = Product(1, "hello", 3.14)
update = Product(2, "world")
modified = original.with_changes(update)
# Result: Product(int=2, str="world", float=3.14)
```

## Documentation

- [Complete Documentation](docs/README.md)
- [Quick Reference](docs/QUICK_REFERENCE.md)
- [Type Hints Reference](docs/TYPE_HINTS_REFERENCE.md)
- [API Documentation](docs/SPECIFICATION_COMPLIANCE.md)

## Examples

See the [examples](examples/) directory for:
- [demo.py](examples/demo.py) - Interactive demonstration
- [type_hint_verification.py](examples/type_hint_verification.py) - Type hint examples

## Testing

```bash
# Run tests
python -m pytest tests/

# Run type checking
mypy product_types/
pyright product_types/
```

## IDE Support

Full support for:
- PyCharm (autocomplete, type checking, navigation)
- VSCode with Pylance (IntelliSense, type hints)
- mypy (static type checking)
- pyright (type analysis)

## Requirements

- Python 3.14+
- typing-extensions >= 4.12.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use this library in academic work, please cite:

```bibtex
@software{product_types,
  title = {Product Types for Python},
  author = {Product Types Contributors},
  year = {2025},
  url = {https://github.com/yourusername/product-types}
}
```
