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
    Any, TypeVar, Generic, TypeVarTuple, Union, get_args, get_origin,
    overload, Protocol, runtime_checkable, Iterator, ClassVar, Unpack
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
    def __new__[NewItemTs](mcs, name:str, v1: Intersection[NewItemTs], **kwargs) -> Intersection[NewItemTs]: ...

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
type _IorT[T] = Intersection[T] | T
type _IorTy[T] = Intersection[T] | type[T]
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

    #
    # NOTE: We enumerate these constructors since it's not possible to homogenize/flatten out any contained Intersection[...] within the args.
    # Ideally, we would be able to write something akin to...
    #   def __new__[*Ts](cls, *vs : Unpack[tuple[*IntersectionOrType[Ts]]) -> Intersection[Union[*Ts]]
    #  
    @overload
    def __new__[T1](cls, v1: _IorT[T1]) -> Intersection[T1]: ...
    @overload
    def __new__[T1, T2](cls, v1: _IorT[T1],v2: _IorT[T2],) -> Intersection[T1 | T2]: ...
    @overload
    def __new__[T1, T2, T3](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],) -> Intersection[T1 | T2 | T3]: ...
    @overload
    def __new__[T1, T2, T3, T4](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],) -> Intersection[T1 | T2 | T3 | T4]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],) -> Intersection[T1 | T2 | T3 | T4 | T5]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],v11: _IorT[T11],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],v11: _IorT[T11],v12: _IorT[T12],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],v11: _IorT[T11],v12: _IorT[T12],v13: _IorT[T13],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],v11: _IorT[T11],v12: _IorT[T12],v13: _IorT[T13],v14: _IorT[T14],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13 | T14]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],v11: _IorT[T11],v12: _IorT[T12],v13: _IorT[T13],v14: _IorT[T14],v15: _IorT[T15],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13 | T14 | T15]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16](cls, v1: _IorT[T1],v2: _IorT[T2],v3: _IorT[T3],v4: _IorT[T4],v5: _IorT[T5],v6: _IorT[T6],v7: _IorT[T7],v8: _IorT[T8],v9: _IorT[T9],v10: _IorT[T10],v11: _IorT[T11],v12: _IorT[T12],v13: _IorT[T13],v14: _IorT[T14],v15: _IorT[T15],v16: _IorT[T16],) -> Intersection[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13 | T14 | T15 | T16]: ...

    def __new__(cls, *vs : Any) -> Intersection[UnionType]: ... 
    """
    NOTE: Runtime types will still track accurately, but for static checking we quit after 16-wide constructor calls.
    You can always do `Intersection(T1,...,T16) & Intersection(T17,...) & ...` if you *really* want all the types.
    """
    #
    #
    #
    
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
    
    #
    # NOTE: For the __class_getitem__, the `OtherItemTs` is not evaluated to a runtime UnionType object, and so the above type hints
    # successfully propagate. Unfortunately, for __getitem__, the type is already evaluated to UnionType before we can intercept it;
    # and while 'TypeForm' should resolve the issue, requiring the caller to annotate with TypeForm[A|B|...] is unacceptable.
    # 
    # Ideally, TypeForm (or perhaps TypeExpr by the time of Python 3.15+) will be able to capture such annotations before they can
    # be evaluated to an opqque UnionType. If this is specified, it's probably in PEP 747.
    #
    def __getitem__[OtherItemTs](self, types: TypeForm[OtherItemTs] | OtherItemTs) -> Intersection[OtherItemTs]:
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

    def to[ItemT](self, typ: type[ItemT]) -> ItemT:
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
