"""
Conjunction Type System - A Progressive, Immutable Tagged Union Type for the best of Products and Intersections.

This module implements a type system where Conjunction[A | B | C] represents
a container holding exactly one value of each type A, B, and C. 

Key Features:
- Immutable, hashable instances
- Full type-level and value-level operations
- Integration with Python's type system via TypeForm/TypeExpr
- Support for subset checking, iteration, and type extraction
- Associative composition via & operator

Usage:
    # Type-level
    type MyType = Conjunction[int | str | float]
    
    # Value-level
    value: MyType = Conjunction(42, "hello", 3.14)
    
    # Extraction
    x: int = value.to(int)
    x, y, z = value.to(int, str, float)
"""

from __future__ import annotations

from typing import Any, Union, get_args, get_origin, Iterator, ClassVar
from typing_extensions import TypeForm  # PEP 747 support
from types import GenericAlias, UnionType
import weakref


#
# type plumbing (runtime inspection)
#
def _normalize_union(tp: Any) -> frozenset[type | GenericAlias]:
    """
    Normalize a type expression into a frozenset of component types.
    
    Handles:
    - Union[A, B, C] -> {A, B, C}
    - A | B | C -> {A, B, C}
    - A -> {A}
    - Conjunction[A | B] -> {A, B}
    - Some[*Targs] -> {Some[*Targs]} (GenericAlias)
    """
    # Handle Conjunction types
    if isinstance(tp, ConjunctionMeta):
        return tp._types
    
    # Handle Union types (both typing.Union and | operator)
    origin = get_origin(tp)
    if origin is Union or isinstance(tp, UnionType):
        args = get_args(tp)
        result = set()
        for arg in args:
            if arg is type(...) or arg is Ellipsis:
                continue
            result.update(_normalize_union(arg))
        return frozenset(result)
    
    # Handle Ellipsis
    if tp is type(...) or tp is Ellipsis:
        return frozenset()
    
    # Single type or GenericAlias
    if isinstance(tp, type) or isinstance(tp, GenericAlias):
        return frozenset([tp])
    
    raise TypeError(f"Cannot normalize type: {tp}")

def _types_equal(types1: frozenset[type], types2: frozenset[type]) -> bool:
    """Check if two type sets are equivalent (permutation invariant)."""
    return types1 == types2

def _format_types(types: frozenset[type | GenericAlias]) -> str:
    """Format a set of types as a union string."""
    if not types:
        return '...'
    return ' | '.join(sorted(t.__name__ for t in types))
#
#
#


#
# conjunction implementation
#
class ConjunctionMeta(type):
    """
    Metaclass for Conjunction that handles type-level operations.
    
    This enables:
    - Conjunction[float | int | str] as a type constructor
    - Type comparison and subset checking
    - Iteration over component types
    - Hashing and equality at the type level
    """
    
    _cache: ClassVar[weakref.WeakValueDictionary] = weakref.WeakValueDictionary()
    """Cache for created Conjunction types to ensure identity."""

    _types: frozenset[type]
    """The types contained by a particular instance of ConjunctionMeta."""
    
    def __new__(
        mcs, 
        name: str, 
        bases: tuple[type, ...], 
        namespace: dict[str, Any],
        types: frozenset[type] | None = None
    ):
        cls = super().__new__(mcs, name, bases, namespace)
        
        # Store the component types
        if types is not None:
            cls._types = types
        elif not hasattr(cls, '_types'):
            cls._types = frozenset()
        
        return cls
    
    def __getitem__(cls, item: TypeForm | Any) -> ConjunctionMeta:
        """
        Type constructor: Conjunction[A | B | C]
        
        Supports:
        - Conjunction[float | int | str]
        - Conjunction[float, int, str] (via tuple unpacking)
        - Conjunction[Conjunction[float] | int] (flattening)
        """
        # Handle tuple notation: Conjunction[A, B, C]
        if isinstance(item, tuple):
            types = set()
            for t in item:
                types.update(_normalize_union(t))
            normalized = frozenset(types)
        else:
            # Single type or union: Conjunction[A | B | C]
            normalized = _normalize_union(item)
        
        # Handle Conjunction[...] - wildcard/open type
        if not normalized:
            # Return the base class for open conjunction
            return cls
        
        # Check cache
        cache_key = normalized
        if cache_key in cls._cache:
            return cls._cache[cache_key]
        
        # Create new Conjunction type
        new_cls = ConjunctionMeta(
            f'Conjunction[{_format_types(normalized)}]',
            (cls,) if cls is Conjunction else (Conjunction,),
            {},
            types=normalized
        )
        
        # Cache it
        cls._cache[cache_key] = new_cls
        return new_cls
    
    def __eq__(cls, other: Any) -> bool:
        """Type equality - permutation invariant."""
        if not isinstance(other, ConjunctionMeta):
            return False
        return _types_equal(cls._types, other._types)
    
    def __hash__(cls) -> int:
        """Hash based on component types (permutation invariant)."""
        return hash(cls._types)
    
    def __contains__(cls, item: type | GenericAlias | ConjunctionMeta) -> bool:
        """
        Check if a type is contained in this Conjunction type.
        
        - float in Conjunction[float | int | str] -> True
        - Conjunction[float | int] in Conjunction[float | int | str] -> True
        - Conjunction[float | dict] in Conjunction[float | int | str] -> False
        """
        if isinstance(item, ConjunctionMeta):
            # Check if all types in item are in cls
            return item._types.issubset(cls._types)
        elif isinstance(item, type):
            return item in cls._types
        else:
            # Handle Generic types
            item_types = _normalize_union(item)
            return item_types.issubset(cls._types)
    
    def __iter__(cls) -> Iterator[type]:
        """Iterate over component types."""
        return iter(cls._types)
    
    def __len__(cls) -> int:
        """Number of component types."""
        return len(cls._types)
    
    def __repr__(cls) -> str:
        if not cls._types:
            return 'Conjunction'
        return f'Conjunction[{_format_types(cls._types)}]'
    
    def __and__(cls, other) -> ConjunctionMeta:
        """
        Type-level conjunction operator.
        
        Conjunction[float] & Conjunction[str] == Conjunction[float | str]
        Conjunction[float] & str == Conjunction[float | str]
        """
        # Check ConjunctionMeta first since it's also isinstance of type
        if isinstance(other, ConjunctionMeta):
            other_types = other._types
        elif isinstance(other, GenericAlias) or isinstance(other, type):
            other_types = frozenset([other])
        else:
            raise TypeError(f"Cannot combine Conjunction with {type(other)}")
        
        combined = cls._types | other_types
        
        # Check cache first
        if combined in cls._cache:
            return cls._cache[combined]
        
        # Create new type directly
        new_cls = ConjunctionMeta(
            f'Conjunction[{_format_types(combined)}]',
            (Conjunction,),
            {},
            types=combined
        )
        
        # Cache it
        cls._cache[combined] = new_cls
        return new_cls
    
    def __rand__(cls, other: type) -> ConjunctionMeta:
        """
        Reverse conjunction operator for: str & Conjunction[float]
        """
        # NOTE: cls.__and__(other) won't work here since we could be inside mcs and not any cls
        return ConjunctionMeta.__and__(cls, other)
    
    def __instancecheck__(cls, instance: Any) -> bool:
        """
        Support isinstance(obj, Conjunction[float | int]).
        
        Checks if obj is an Conjunction instance with matching types.
        """
        # Use type() to avoid recursion (don't call isinstance)
        if not (type(instance).__class__ is ConjunctionMeta or 
                type(instance) is Conjunction or
                issubclass(type(instance), Conjunction)):
            return False
        
        # For base Conjunction class, any Conjunction instance matches
        if not cls._types:
            return True
        
        # Check if instance's types match this type's types
        instance_types = frozenset(instance._data.keys())
        return instance_types == cls._types
    
    def __subclasscheck__(cls, subclass: Any) -> bool:
        """
        Support issubclass(Conjunction[A | B], Conjunction[A | B | C]).
        
        A subclass has a subset of types (or equal).
        """
        if not isinstance(subclass, ConjunctionMeta):
            return False
        
        # Subclass has subset of types
        return subclass._types.issubset(cls._types)


class Conjunction(metaclass=ConjunctionMeta):
    """
    Immutable container holding exactly one value for each component type.
    
    This is the base class for all Conjunction instances. Specific type
    combinations create subclasses via the metaclass.
    
    Attributes:
        _data: Immutable mapping from type to value
        _hash: Cached hash value
    """
    
    __slots__ = ('_data', '_hash')
    
    def __init__(self, *values: Any, **kwargs: Any):
        """
        Create an Conjunction instance from values.
        
        Args:
            *values: Values to store, types are inferred
            **kwargs: Alternative specification as type=value pairs
        
        Examples:
            Conjunction(5, "hello", 3.14)
            Conjunction(int=5, str="hello", float=3.14)
            Conjunction(existing_conjunction, 42)
        """
        # Handle immutability
        if hasattr(self, '_data'):
            raise TypeError("Conjunction instances are immutable")
        
        data: dict[type, Any] = {}
        
        # Process positional arguments
        for value in values:
            # If it's already an Conjunction, merge it (associativity)
            if isinstance(value, Conjunction):
                for typ, val in value._data.items():
                    if typ in data:
                        # Right-most value takes precedence
                        data[typ] = val
                    else:
                        data[typ] = val
            else:
                # Infer type from value
                typ = type(value)
                if typ in data:
                    # Right-most value takes precedence (associativity)
                    data[typ] = value
                else:
                    data[typ] = value
        
        # Process keyword arguments (explicit type specification)
        for typ, value in kwargs.items():
            if not isinstance(typ, type):
                # Try to evaluate as string type name
                try:
                    typ = eval(typ)
                except:
                    raise TypeError(f"Invalid type specification: {typ}")
            
            if typ in data:
                data[typ] = value
            else:
                data[typ] = value
        
        # Make immutable
        object.__setattr__(self, '_data', data)
        object.__setattr__(self, '_hash', None)
    
    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent attribute modification (immutability)."""
        raise TypeError("Conjunction instances are immutable")
    
    def __delattr__(self, name: str) -> None:
        """Prevent attribute deletion (immutability)."""
        raise TypeError("Conjunction instances are immutable")
    
    def __getitem__(self, types: TypeForm | tuple[type, ...]) -> Conjunction:
        """
        Extract a subset of types, returning a new Conjunction.
        
        Args:
            types: Single type, union of types, or tuple of types
        
        Returns:
            New Conjunction with only the requested types
        
        Raises:
            KeyError: If any requested type is not present
        
        Examples:
            obj[float] -> Conjunction[float]
            obj[float | int] -> Conjunction[float | int]
        """
        # Normalize input to set of types
        if isinstance(types, tuple):
            type_set = set()
            for t in types:
                type_set.update(_normalize_union(t))
        else:
            type_set = _normalize_union(types)
        
        # Check all types are present
        missing = type_set - set(self._data.keys())
        if missing:
            raise KeyError(f"Types not in Conjunction: {missing}")
        
        # Extract subset
        new_data = {t: self._data[t] for t in type_set}
        result = Conjunction.__new__(Conjunction)
        object.__setattr__(result, '_data', new_data)
        object.__setattr__(result, '_hash', None)
        return result
    
    def __contains__(self, item: type | TypeForm) -> bool:
        """
        Check if a type is present in this instance.
        
        Examples:
            float in obj -> True if obj has a float value
            float | int in obj -> True if obj has both float and int values
        """
        types = _normalize_union(item)
        return types.issubset(set(self._data.keys()))
    
    def __iter__(self) -> Iterator[type]:
        """Iterate over types (keys)."""
        return iter(self._data.keys())
    
    def keys(self) -> Iterator[type]:
        """Iterate over types."""
        return iter(self._data.keys())
    
    def values(self) -> Iterator[Conjunction]:
        """
        Iterate over values, each wrapped as Conjunction[T].
        
        This maintains type safety by keeping values in Conjunction containers.
        """
        for typ, value in self._data.items():
            wrapped = Conjunction.__new__(Conjunction)
            object.__setattr__(wrapped, '_data', {typ: value})
            object.__setattr__(wrapped, '_hash', None)
            yield wrapped
    
    def items(self) -> Iterator[tuple[type, Conjunction]]:
        """
        Iterate over (type, value) pairs.
        
        Values are wrapped as Conjunction[T] for type safety.
        """
        for typ, value in self._data.items():
            wrapped = Conjunction.__new__(Conjunction)
            object.__setattr__(wrapped, '_data', {typ: value})
            object.__setattr__(wrapped, '_hash', None)
            yield (typ, wrapped)
    
    def to(self, typ: type) -> Any:
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
        if typ not in self._data:
            raise KeyError(f"Type {typ} not in Conjunction")
        return self._data[typ]
     
    def __and__(self, other: Any) -> Conjunction:
        """
        Combine with another Conjunction or any value (associative, right-precedence).
        
        self & other creates a new Conjunction with values from both.
        If other is not an Conjunction, it's wrapped in one first.
        If types overlap, right-side (other) takes precedence.
        
        Examples:
            Conjunction(5) & Conjunction("hello") == Conjunction(5, "hello")
            Conjunction(5) & "hello" == Conjunction(5, "hello")
        """
        # If other is not an Conjunction, wrap it
        if not (type(other).__class__ is ConjunctionMeta or 
                type(other) is Conjunction or
                (isinstance(other, type) and issubclass(other, Conjunction))):
            other = Conjunction(other)
        
        # Combine data (right takes precedence)
        new_data = {**self._data, **other._data}
        result = Conjunction.__new__(Conjunction)
        object.__setattr__(result, '_data', new_data)
        object.__setattr__(result, '_hash', None)
        return result
    
    def __rand__(self, other: Any) -> Conjunction:
        """
        Reverse & operator: value & Conjunction
        """
        return Conjunction.__and__(self, other)
    
    def __truediv__(self, types: type | TypeForm) -> Conjunction:
        """
        Set difference - return a new Conjunction without a type.
        
        Examples:
            obj / bool -> Removes bool type if present
            obj / (bool | str) -> Removes bool and str types
        """
        type_set = _normalize_union(types)
        new_data = {t: v for t, v in self._data.items() if t not in type_set}
        
        result = Conjunction.__new__(Conjunction)
        object.__setattr__(result, '_data', new_data)
        object.__setattr__(result, '_hash', None)
        return result
    
    def __eq__(self, other: Any) -> bool:
        """Equality: same types and same values."""
        if not isinstance(other, Conjunction):
            return False
        
        if set(self._data.keys()) != set(other._data.keys()):
            return False
        
        for typ in self._data:
            if self._data[typ] != other._data[typ]:
                return False
        
        return True
    
    def __hash__(self) -> int:
        """
        Hash based on types and values (for set/dict usage).
        
        Cached for performance.
        """
        if self._hash is not None:
            return self._hash
        
        # Hash based on frozenset of (type, hash(value)) pairs
        items = []
        for typ, value in self._data.items():
            try:
                items.append((typ, hash(value)))
            except TypeError:
                # Value is unhashable - use id instead
                items.append((typ, id(value)))
        
        h = hash(frozenset(items))
        object.__setattr__(self, '_hash', h)
        return h
    
    def __repr__(self) -> str:
        """String representation showing types and values."""
        if not self._data:
            return 'Conjunction()'
        
        items = [f'{typ.__name__}={repr(val)}' for typ, val in self._data.items()]
        return f'Conjunction({", ".join(items)})'
    
    def __len__(self) -> int:
        """Number of component values."""
        return len(self._data)
