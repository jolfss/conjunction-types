# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**conjunction-types** is a Python library implementing a sophisticated type system that combines intersection and product type features. The `Conjunction[A | B | C]` type represents an immutable container holding exactly one value of each type A, B, and C.

This is a typing-focused library targeting Python 3.12+ with extensive static type hints (`.pyi` stub files) to enable precise type checking with Pyright.

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run tests with verbose output (default configuration)
pytest -v

# Run a specific test function
pytest tests/test.py::test_type_subset_checking

# Run tests with type checking first
pyright && pytest
```

### Type Checking
```bash
# Run Pyright type checker (configured for Python 3.14, standard mode)
pyright

# Check specific file
pyright conjunction_types/_core.py
```

### Building
```bash
# Build the package
python -m build

# Install in development mode
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"
```

## Architecture

### Core Components

**[conjunction_types/_core.py](conjunction_types/_core.py)**: The complete runtime implementation (~550 lines)
- `ConjunctionMeta`: Metaclass handling type-level operations (type construction, caching, subset checking, iteration)
- `Conjunction`: Base class for instances (value storage, extraction, composition, immutability)
- `_normalize_union()`: Type normalization handling Union types, UnionType (PEP 604), and flattening nested Conjunctions

**[conjunction_types/_core.pyi](conjunction_types/_core.pyi)**: Static type hints stub file (~150 lines)
- Contains extensive `@overload` declarations for `__new__` (16 overloads for different arities)
- Provides generic type parameter propagation that's impossible to express in pure runtime Python
- Workaround for Pyright's evaluation of union types: uses `__class_getitem__` to intercept type parameter before evaluation to `UnionType`

### Key Design Patterns

1. **Metaclass-based Type System**: `ConjunctionMeta` enables `Conjunction[A | B]` syntax and type-level operations like subset checking (`A in Conjunction[A | B | C]`)

2. **WeakValueDictionary Caching**: Type instances are cached by their frozenset of component types to ensure type identity (`Conjunction[A | B] is Conjunction[B | A]`)

3. **Dual Implementation Strategy**: Runtime behavior in `.py`, static type hints in `.pyi` to work around Python's typing limitations

4. **Type Normalization**: All type inputs (Union, UnionType, GenericAlias, nested Conjunctions) normalize to `frozenset[type]` for consistent comparison

5. **Immutability via `__slots__`**: Instances use `__slots__ = ('_data', '_hash')` with `object.__setattr__` to enforce immutability while allowing initialization

6. **Right-Precedence Composition**: The `&` operator is associative but not commutative - when combining instances with overlapping types, the rightmost value wins

### Critical Type Checking Workarounds

The `.pyi` file contains several workarounds for Pyright limitations:

- **Lines 24-37**: Commented explanation of why `__class_getitem__` must be used instead of metaclass `__getitem__` for proper type parameter capture
- **Lines 62-102**: Manual enumeration of 16 `__new__` overloads since TypeVarTuple cannot properly flatten `Conjunction[A] | B | Conjunction[C]` into the union type parameters
- **Line 115**: `__class_getitem__` successfully captures `OtherItemTs` before Pyright evaluates it to opaque `UnionType`

## Testing Philosophy

The test suite in [tests/test.py](tests/test.py) is comprehensive and serves as both validation and documentation:

- Tests are organized by feature (type checking, construction, extraction, operators, immutability, etc.)
- Each test includes descriptive comments and assertion messages
- Tests cover both type-level operations (on `ConjunctionMeta`) and instance-level operations
- Edge cases include empty Conjunctions, single-type Conjunctions, nested merging, and type override behavior

## Development Notes

- This is a pure-Python library with no runtime dependencies
- The library uses modern Python typing features: PEP 695 (type parameters), PEP 604 (union operator), PEP 747 mentions
- Generic types like `dict[str, int]` are fully supported and distinguished at the type level
- The metaclass `__instancecheck__` and `__subclasscheck__` enable `isinstance()` and `issubclass()` with Conjunction types
- Hash caching is used for performance since Conjunction instances are immutable
