"""
Intersection Type System - A Progressive, Immutable Tagged Union Type

This module implements a type system where Intersection[A | B | C] represents
a container holding exactly one value of each type A, B, and C. Despite the name
"Intersection", this is semantically a product type (tuple of typed values) rather
than a type intersection in the traditional sense.

Key Features:
- Immutable, hashable instances
- Full type-level and value-level operations
- Integration with Python's type system via TypeForm/TypeExpr
- Support for subset checking, iteration, and type extraction
- Associative composition via & operator

Usage:
    # Type-level
    type MyType = Intersection[int | str | float]
    
    # Value-level
    value: MyType = Intersection(42, "hello", 3.14)
    
    # Extraction
    x: int = value.to(int)
    x, y, z = value.to(int, str, float)
"""

from __future__ import annotations

import sys
from typing import (
    Any, TypeVar, Generic, Union, get_args, get_origin,
    overload, Protocol, runtime_checkable, Iterator, ClassVar
)
from typing_extensions import TypeForm  # PEP 747 support
from collections.abc import Iterable
from types import UnionType
import weakref


__all__ = ['Intersection', 'IntersectionMeta']

# ============================================================================
# Type Utilities
# ============================================================================

def _normalize_union(tp: Any) -> frozenset[type]:
    """
    Normalize a type expression into a frozenset of component types.
    
    Handles:
    - Union[A, B, C] -> {A, B, C}
    - A | B | C -> {A, B, C}
    - A -> {A}
    - Intersection[A | B] -> {A, B}
    """
    ...


def _types_equal(types1: frozenset[type], types2: frozenset[type]) -> bool:
    """Check if two type sets are equivalent (permutation invariant)."""
    ...

# ============================================================================
# Intersection Metaclass - Handles Type-Level Operations
# ============================================================================

class IntersectionMeta[ItemTs](type):
    """
    Metaclass for Intersection that handles type-level operations.
    
    This enables:
    - Intersection[float | int | str] as a type constructor
    - Type comparison and subset checking
    - Iteration over component types
    - Hashing and equality at the type level
    """
    
    # Cache for created Intersection types to ensure identity
    _cache: ClassVar[weakref.WeakValueDictionary]
    @overload
    def __new__[T1](mcs, name:str, v1: Intersection[T1], **kwargs) -> Intersection[T1]: ...

    @overload
    def __new__(
        mcs, 
        name: str, 
        bases: tuple[type, ...], 
        namespace: dict[str, Any],
        types: frozenset[type] | None = None
    ) -> Intersection[ItemTs]:
        ...

    # NOTE: Pyright evaluates the raw `OtherItemTs` in the Intersection class, so by the time we get to this metaclass
    # call, A | B | C has already evaluated to UnionType (which has no type parameters to inspect). Thus, to satisfy
    # the type checker, we override __class_getitem__ in Intersection to provide annotations.
    #
    # def __getitem__[OtherItemTs](cls, item: TypeForm[OtherItemTs] | OtherItemTs) -> IntersectionMeta[OtherItemTs]:
    #     """
    #     Type constructor: Intersection[A | B | C]
        
    #     Supports:
    #     - Intersection[float | int | str]
    #     - Intersection[float, int, str] (via tuple unpacking)
    #     - Intersection[Intersection[float] | int] (flattening)
    #     """
    #     ...
    
    def __eq__(cls, other: Any) -> bool:
        """Type equality - permutation invariant."""
        ...
    
    def __hash__(cls) -> int:
        """Hash based on component types (permutation invariant)."""
        ...

    def __contains__[OtherItemTs](cls, item: type | IntersectionMeta[OtherItemTs]) -> bool:
        """
        Check if a type is contained in this Intersection type.
        
        - float in Intersection[float | int | str] -> True
        - Intersection[float | int] in Intersection[float | int | str] -> True
        - Intersection[float | dict] in Intersection[float | int | str] -> False
        """
        ...

    def __iter__(cls) -> Iterator[type]:
        """Iterate over component types."""
        ...

    def __len__(cls) -> int:
        """Number of component types."""
        ... 
    
    def __repr__(cls) -> str:
        ...
    
    @overload
    def __and__[OtherTs](cls, other: Intersection[OtherTs]) -> IntersectionMeta[ItemTs | OtherTs]: ...

    @overload
    def __and__[OtherTs](cls, other: OtherTs) -> IntersectionMeta[ItemTs | OtherTs]: ...

    def __and__(cls, other: Any) -> IntersectionMeta[Any]:
        """
        Type-level intersection operator.
        
        Intersection[float] & Intersection[str] == Intersection[float | str]
        Intersection[float] & str == Intersection[float | str]
        """
        ...
    
    def __rand__[OtherItemTs](cls, other: type[OtherItemTs]) -> IntersectionMeta[ItemTs | OtherItemTs]:
        """
        Reverse intersection operator for: str & Intersection[float]
        """
        ...
    
    def __instancecheck__(cls, instance: Any) -> bool:
        """
        Support isinstance(obj, Intersection[float | int]).
        
        Checks if obj is an Intersection instance with matching types.
        """
        ...

    def __subclasscheck__(cls, subclass: Any) -> bool:
        """
        Support issubclass(Intersection[A | B], Intersection[A | B | C]).
        
        A subclass has a subset of types (or equal).
        """
        ...

# ============================================================================
# Intersection Class - Handles Value-Level Operations
# ============================================================================
class Intersection[ItemTs](metaclass=IntersectionMeta):
    """
    Immutable container holding exactly one value for each component type.
    
    This is the base class for all Intersection instances. Specific type
    combinations create subclasses via the metaclass.
    
    Attributes:
        _data: Immutable mapping from type to value
        _hash: Cached hash value
    """
    
    __slots__ = ('_data', '_hash')

    def __new__[Ts](cls, *vs : Intersection[Ts] | Ts) -> Intersection[Ts]: ...
    
    def __init__[IncomingItemTs](self, *values: IncomingItemTs, **kwargs: IncomingItemTs) -> None:
        """
        Create an Intersection instance from values.
        
        Args:
            *values: Values to store, types are inferred
            **kwargs: Alternative specification as type=value pairs
        
        Examples:
            Intersection(5, "hello", 3.14)
            Intersection(int=5, str="hello", float=3.14)
            Intersection(existing_intersection, 42)
        """
        ...
    
    def __setattr__(self, name: str, value: ItemTs) -> None:
        """Prevent attribute modification (immutability)."""
        ...
    
    def __delattr__(self, name: str) -> None:
        """Prevent attribute deletion (immutability)."""
        ...

    @classmethod
    def __class_getitem__[OtherItemTs](cls, item: TypeForm[OtherItemTs] | OtherItemTs) -> IntersectionMeta[OtherItemTs]: ...
    
    def __getitem__[ItemT](self, types: type[ItemT] | TypeForm[ItemT] | tuple[type[ItemTs], ...]) -> Intersection[ItemTs]:
        """
        Extract a subset of types, returning a new Intersection.
        
        Args:
            types: Single type, union of types, or tuple of types
        
        Returns:
            New Intersection with only the requested types
        
        Raises:
            KeyError: If any requested type is not present
        
        Examples:
            obj[float] -> Intersection[float]
            obj[float | int] -> Intersection[float | int]
        """
        ...
    
    def __contains__(self, item: type[ItemTs] | TypeForm[ItemTs]) -> bool:
        """
        Check if a type is present in this instance.
        
        Examples:
            float in obj -> True if obj has a float value
            float | int in obj -> True if obj has both float and int values
        """
        ...

    def __iter__(self) -> Iterator[type[ItemTs]]:
        """Iterate over types (keys)."""
        ... 
    
    def keys(self) -> Iterator[type[ItemTs]]:
        """Iterate over types."""
        ...
    
    def values(self) -> Iterator[Intersection[ItemTs]]:
        """
        Iterate over values, each wrapped as Intersection[T].
        
        This maintains type safety by keeping values in Intersection containers.
        """
        ...

    def items(self) -> Iterator[tuple[type, Intersection[ItemTs]]]:
        """
        Iterate over (type, value) pairs.
        
        Values are wrapped as Intersection[T] for type safety.
        """
        ...

    @overload
    def to[ItemT](self, typ: type[ItemT]) -> ItemT: ...
    
    @overload
    def to[ManyItemT](self, *types: type[ManyItemT]) -> tuple[ManyItemT]: ...
    
    def to(self, *types: type) -> Any:
        """
        Extract raw values by type.
        
        Args:
            *types: One or more types to extract
        
        Returns:
            Single value if one type given, tuple of values if multiple
        
        Raises:
            KeyError: If any type is not present
        
        Examples:
            obj.to(float) -> 3.14
            obj.to(float, int, str) -> (3.14, 5, "hello")
        """
        ...
    
    @overload
    def __and__[OtherItemTs](self, other: Intersection[OtherItemTs]) -> Intersection[ItemTs | OtherItemTs]: ...

    @overload
    def __and__[OtherItemTs](self, other: OtherItemTs) -> Intersection[ItemTs | OtherItemTs]:
        """
        Combine with another Intersection or any value (associative, right-precedence).
        
        self & other creates a new Intersection with values from both.
        If other is not an Intersection, it's wrapped in one first.
        If types overlap, right-side (other) takes precedence.
        
        Examples:
            Intersection(5) & Intersection("hello") == Intersection(5, "hello")
            Intersection(5) & "hello" == Intersection(5, "hello")
        """
        ...
    
    def __rand__[OtherItemT](self, other: OtherItemT) -> Intersection[ItemTs | OtherItemT]:
        """
        Reverse & operator: value & Intersection
        """
        ...
    
    def __truediv__(self, types: type | TypeForm[Any]) -> Intersection[Any]:
        """
        Set difference - remove types from this Intersection.
        
        This is a bonus feature for filtering out unwanted types.
        
        Examples:
            obj / bool -> Removes bool type if present
            obj / (bool | str) -> Removes bool and str types
        """
        ...
    
    def __eq__(self, other: Any) -> bool:
        """
        Equality: same types and same values.
        
        Note: Values are compared using ==, so must be comparable.
        """
        ...

    def __hash__(self) -> int:
        """
        Hash based on types and values (for set/dict usage).
        
        Cached for performance.
        """
        ...
    
    def __repr__(self) -> str:
        """String representation showing types and values."""
        ...
    
    def __len__(self) -> int:
        """Number of component values."""
        ...

# ============================================================================
# Utility Functions
# ============================================================================

def _format_types(types: frozenset[type]) -> str:
    """Format a set of types as a union string."""
    ...
