# Product Types - Complete Type Hints Reference

This document shows all the type hints defined in the Product type system, demonstrating full IDE inspectability.

## Module-Level Type Hints

```python
from typing_extensions import TypeForm as TypeExpr
```

All generic type parameters use `TypeExpr` (PEP 747) for proper type form support.

## ProductMeta Class Type Hints

The metaclass has full type annotations matching the original specification:

```python
class ProductMeta[ProductTs: TypeExpr](type):
    _types: frozenset[type]
    _name: str
    
    def __new__(
        mcs, 
        name: str, 
        bases: tuple[type, ...], 
        namespace: dict[str, Any], 
        types: frozenset[type] | None = None, 
        **kwargs: Any
    ) -> 'ProductMeta[ProductTs]': ...
    
    def __init__(
        cls, 
        name: str, 
        bases: tuple[type, ...], 
        namespace: dict[str, Any], 
        **kwargs: Any
    ) -> None: ...
    
    def __getitem__[DivisorTs: TypeExpr](
        cls, 
        divisor_types: DivisorTs
    ) -> 'ProductMeta[DivisorTs]': ...
    
    def __call__(
        cls, 
        *args: Any, 
        **kwargs: Any
    ) -> 'Product[ProductTs]': ...
    
    def __eq__(cls, other: object) -> bool: ...
    
    def __hash__(cls) -> int: ...
    
    def __and__[IncomingTs: TypeExpr](
        cls, 
        other: 'Product[IncomingTs] | ProductMeta[IncomingTs]'
    ) -> 'ProductMeta[ProductTs | IncomingTs]': ...
    
    def __contains__(cls, item: Any) -> bool: ...
    
    def __repr__(cls) -> str: ...
    
    def __str__(cls) -> str: ...
```

## Product Class Type Hints

The Product class has full type annotations:

```python
class Product[ProductTs: TypeExpr](metaclass=ProductMeta):
    _values: dict[type, Any]
    
    def __new__(
        cls, 
        *args: Any, 
        **kwargs: Any
    ) -> 'Product[ProductTs]': ...
    
    def __init__(self, *args: ProductTs) -> None: ...
    
    # Overloaded for precise return types
    @overload
    def __getitem__(self, key: type) -> Any: ...
    
    @overload
    def __getitem__[DivisorTs: TypeExpr](
        self, 
        key: DivisorTs
    ) -> 'Product': ...
    
    def __getitem__[DivisorTs: TypeExpr](
        self, 
        key: type | DivisorTs
    ) -> 'Any | Product': ...
    
    def __setitem__(self, key: type, value: Any) -> None: ...
    
    def __and__[IncomingTs: TypeExpr](
        self, 
        other: 'Product[IncomingTs] | IncomingTs'
    ) -> 'Product[ProductTs | IncomingTs]': ...
    
    def with_changes(self, *args: Any) -> 'Product[ProductTs]': ...
    
    def __eq__(self, other: object) -> bool: ...
    
    def __hash__(self) -> int: ...
    
    def __repr__(self) -> str: ...
    
    def __str__(self) -> str: ...
```

## Helper Function Type Hints

```python
def make_product_type(*types: type) -> ProductMeta:
    """Create a Product type from a list of types."""
    ...
```

## Usage Examples with Type Hints

### Variable Annotations

```python
# Type-annotated Product type
IntStrFloat: ProductMeta[int | str | float] = Product[int | str | float]

# Type-annotated Product instance
my_product: Product[int | str | float] = Product(42, "hello", 3.14)

# Type-annotated value access
int_value: int = my_product[int]
str_value: str = my_product[str]

# Type-annotated subset access
subset: Product[int | str] = my_product[int | str]
```

### Function Signatures

```python
def process_product(p: Product[int | str | float]) -> int:
    """IDE will show full type information."""
    return p[int] * 2

def create_product(i: int, s: str, f: float) -> Product[int | str | float]:
    """IDE will show return type."""
    return Product(i, s, f)

def get_type_constructor() -> ProductMeta[int | str]:
    """IDE will show ProductMeta return type."""
    return Product[int | str]
```

### Class Definitions

```python
class MyProduct(Product[int | str | bool]):
    """Custom Product with methods."""
    
    def get_int_value(self) -> int:
        """IDE shows return type is int."""
        return self[int]
    
    def get_str_value(self) -> str:
        """IDE shows return type is str."""
        return self[str]

# Type-annotated instance creation
instance: MyProduct = MyProduct(42, "test", True)
value: int = instance.get_int_value()
```

### Type Operations

```python
# Type division
Base: ProductMeta[int | str | float] = Product[int | str | float]
Subset: ProductMeta[int | str] = Base[int | str]

# Type composition
T1: ProductMeta[int] = Product[int]
T2: ProductMeta[str] = Product[str]
Combined: ProductMeta[int | str] = T1 & T2

# Type extension
Extended: ProductMeta[int | str | float] = Product[Combined | float]
```

### Instance Operations

```python
# Instance composition
p1: Product[int | str] = Product(1, "hello")
p2: Product[float | bool] = Product(3.14, True)
combined: Product[int | str | float | bool] = p1 & p2

# with_changes
original: Product[int | str] = Product(1, "hello")
update: Product[int | str] = Product(2, "world")
modified: Product[int | str] = original.with_changes(update)
```

## IDE Support

All type hints follow Python 3.14+ standards and will be recognized by:

- **PyCharm**: Full autocomplete, type checking, and navigation
- **VSCode with Pylance**: Complete IntelliSense and type hints
- **mypy**: Static type checking (with appropriate stubs)
- **pyright**: Type checking and analysis
- **Other type-aware IDEs**: Any IDE that supports PEP 695 and PEP 747

## Type System Features

The type hints enable:

1. **Autocomplete**: IDEs show available methods and attributes
2. **Type Checking**: Static analysis catches type errors
3. **Navigation**: Jump to definition works for all types
4. **Refactoring**: Safe rename and refactor operations
5. **Documentation**: Hover shows full type information
6. **Error Detection**: Catch mistakes before runtime

## Key Type Relationships

```python
# These relationships are properly typed:
Product[int | str] <: Product[int | str | float]  # Subtype relation
Product[int] & Product[str] == Product[int | str]  # Type equality
Product[Product[int] | str] == Product[int | str]  # Flattening
```

## Generic Type Parameters

The implementation uses PEP 695 syntax for generic type parameters:

- `ProductTs: TypeExpr` - The types contained in a Product
- `DivisorTs: TypeExpr` - Types extracted via type division
- `IncomingTs: TypeExpr` - Types being added via & operator

These enable precise type tracking through all operations.

## Testing Type Hints

Run `type_hint_verification.py` to verify all type hints work:

```bash
python type_hint_verification.py
```

This will exercise all type annotations and confirm IDE inspectability.
