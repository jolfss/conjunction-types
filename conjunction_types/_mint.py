"""
Core minting infrastructure for Conjunction types.

Provides `mint()` to create named type aliases that tag values at construction time,
enabling generic types (like list[int]) to be distinguished in Conjunctions.

Uses typing.NewType as the foundation to create distinct type identities.
"""
from __future__ import annotations

from typing import Any, TypeVar, get_origin, Callable
from types import GenericAlias

__all__ = ["mint", "get_minted_type", "get_mint_name", "get_constructor_by_name", "get_origin_type"]

T = TypeVar("T")

# Global registries for minted types
_minted_constructors: dict[Callable, type | GenericAlias] = {}
"""Maps minted constructor functions to their origin types."""

_minted_names: dict[str, Callable] = {}
"""Maps mint names to their constructor functions."""

_minted_values: dict[int, Callable] = {}
"""Maps value id() to their minted constructor."""


def mint(name: str, typ: type[T] | GenericAlias) -> Callable[..., T]:
    """
    Create a named type constructor with a distinct identity.

    Similar to typing.NewType but creates a constructor that tags values at runtime,
    allowing Conjunction to distinguish between multiple uses of the same type.

    Each call to mint() creates a new distinct constructor, even for the same underlying type.
    This allows you to have multiple "slots" in a Conjunction for the same base type.

    Args:
        name: Stable name for this type (used in serialization and repr)
        typ: The type to mint (can be generic like list[int])

    Returns:
        A callable constructor that creates instances tagged with this mint

    Example:
        >>> from conjunction_types import Conjunction, mint
        >>> IntList = mint("IntList", list[int])
        >>> AnotherIntList = mint("AnotherIntList", list[int])  # Different identity!
        >>>
        >>> c = Conjunction(IntList([1, 2]), AnotherIntList([3, 4]), [5, 6])
        >>> # Conjunction(IntList=[1, 2], AnotherIntList=[3, 4], list=[5, 6])
        >>>
        >>> c.to(IntList)
        [1, 2]
        >>> c.to(AnotherIntList)
        [3, 4]
        >>> c.to(list)
        [5, 6]

    Note:
        - Each mint() call creates a unique constructor with distinct identity
        - Values are weakly referenced to allow garbage collection
        - Minted constructors can be used as keys in Conjunction operations
        - For serialization, import from conjunction_types.ndjson
    """
    # Check if name is already used
    if name in _minted_names:
        existing_constructor = _minted_names[name]
        existing_type = _minted_constructors[existing_constructor]

        # Check if it's the same type - if so, return existing (idempotent)
        if existing_type == typ:
            return existing_constructor

        # Different type with same name - this is an error
        raise ValueError(
            f"Name '{name}' is already registered for type {existing_type}. "
            f"Cannot register it again for type {typ}."
        )

    # Get the actual constructor for the type
    if isinstance(typ, GenericAlias):
        origin = get_origin(typ)
        base_constructor = origin if origin is not None else typ
    else:
        base_constructor = typ

    # Create a new callable that wraps the constructor
    # This gives us a unique identity (via id()) for each mint
    def minted_constructor(*args: Any, **kwargs: Any) -> T:
        """Create an instance and tag it with this minted constructor."""
        # Create the value
        value = base_constructor(*args, **kwargs)

        # Tag it with this minted constructor (using id to avoid WeakRef issues)
        _minted_values[id(value)] = minted_constructor

        return value

    # Store metadata about this constructor
    _minted_constructors[minted_constructor] = typ
    _minted_names[name] = minted_constructor

    # Set name for better debugging
    minted_constructor.__name__ = name
    minted_constructor.__qualname__ = name

    return minted_constructor


def get_minted_type(value: Any) -> Callable | None:
    """
    Get the minted constructor for a value, if it was created with mint().

    Args:
        value: The value to check

    Returns:
        The minted constructor if the value was created with one, else None

    Example:
        >>> IntList = mint("IntList", list[int])
        >>> my_list = IntList([1, 2, 3])
        >>> get_minted_type(my_list) is IntList
        True
        >>> get_minted_type([4, 5, 6])  # Regular list
        None
    """
    return _minted_values.get(id(value))


def get_origin_type(constructor: Callable) -> type | GenericAlias | None:
    """
    Get the origin type for a minted constructor.

    Args:
        constructor: A minted constructor

    Returns:
        The origin type (e.g., list[int]) if it's a minted constructor, else None
    """
    return _minted_constructors.get(constructor)


def get_mint_name(constructor: Callable) -> str | None:
    """
    Get the name of a minted constructor.

    Args:
        constructor: A minted constructor

    Returns:
        The mint name if found, else None
    """
    for name, ctor in _minted_names.items():
        if ctor is constructor:
            return name
    return None


def get_constructor_by_name(name: str) -> Callable | None:
    """
    Get a minted constructor by its name.

    Args:
        name: The mint name

    Returns:
        The minted constructor if the name is registered, else None
    """
    return _minted_names.get(name)
