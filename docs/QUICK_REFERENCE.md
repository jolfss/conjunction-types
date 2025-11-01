# Product Types - Quick Reference

## Import
```python
from product_types import Product, make_product_type
```

## Creating Products

### Direct instantiation
```python
p = Product(5, "hello", 3.14)  # Product[int | str | float]
```

### With explicit type
```python
MyType = Product[int | str | float]
p = MyType(5, "hello", 3.14)
```

### Named class
```python
class MyProduct(Product[int | str | bool]):
    pass

p = MyProduct(42, "test", True)
```

### Helper function
```python
MyType = make_product_type(int, str, float)
p = MyType(5, "hello", 3.14)
```

## Accessing Values

### Single value
```python
p[int]     # Get int value
p[str]     # Get str value
p[int] = 6 # Set int value
```

### Multiple values (creates new Product)
```python
subset = p[int | str]  # Product[int | str]
```

## Type Operations

### Type division (subset extraction)
```python
FullType = Product[int | str | float | bool]
Subset = FullType[int | str]  # Product[int | str]
```

### Type composition (combining)
```python
T1 = Product[int] & Product[str]      # Product[int | str]
T2 = Product[int | str] & Product[float]  # Product[int | str | float]
```

### Type extension
```python
Base = Product[int | str]
Extended = Product[Base | bool]  # Product[int | str | bool]
```

## Instance Operations

### Combining instances
```python
p1 = Product(1, "hello")
p2 = Product(3.14, True)
combined = p1 & p2  # Product with all four values
```

### Updating with changes
```python
original = Product(1, "hello", 3.14)
update = Product(2, "world")
modified = original.with_changes(update)  # int and str updated
```

## Comparisons and Checks

### Equality (permutation invariant)
```python
Product(1, "hi") == Product("hi", 1)  # True
```

### Type containment
```python
int in Product[int | str]              # True
Product[int] in Product[int | str]     # True
Product[int | str] in Product[int]     # False
```

### Type equality
```python
Product[int | str] == Product[str | int]  # True (permutation invariant)
```

## Key Properties

1. **Permutation Invariance**: Order doesn't matter
   - `Product(1, "hi") == Product("hi", 1)`

2. **Type Flattening**: Nested Products are flattened
   - `Product[Product[int | str] | float] == Product[int | str | float]`

3. **Unique Types**: Each type appears at most once
   - Multiple values of same type: last one wins

4. **Type Safety**: Values are indexed by their actual type

## Common Patterns

### Building incrementally
```python
data = Product(1, "hello")
data = data & Product(3.14)
data = data & Product(True)
# Result: Product[int | str | float | bool]
```

### Selective updates
```python
current = Product(1, "hello", 3.14)
updates = Product(2, "world")  # Only update int and str
new = current.with_changes(updates)
# Result: Product(int=2, str="world", float=3.14)
```

### Type-safe storage
```python
# Each value is indexed by its type
cache = Product(42, "cache_key", True, 3.14)

# Access by type, not by position
id = cache[int]
key = cache[str]
enabled = cache[bool]
timeout = cache[float]
```

### Domain modeling
```python
# Define domain types
UserId = Product[int]
UserName = Product[str]
IsActive = Product[bool]

# Combine for complete model
User = Product[UserId | UserName | IsActive]
# Equivalent to: Product[int | str | bool]

user = User(12345, "Alice", True)
```

## Type Hints (Python 3.14+)

```python
from typing_extensions import TypeForm as TypeExpr

def process_data(data: Product[int | str | float]) -> int:
    """Process a Product containing int, str, and float."""
    return data[int] * 2

# Variable annotations
my_product: Product[int | str] = Product(42, "test")
```

## Tips

- Use type division (`[...]`) to create subtypes
- Use `&` to combine types or instances
- Use `with_changes()` for functional updates
- Remember: `|` inside `Product[...]` means intersection, not union
- All nested Products are automatically flattened
- Order never matters - Products are permutation invariant
