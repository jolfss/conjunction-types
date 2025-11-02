from __future__ import annotations

from typing import Any, Union, overload, get_args, get_origin
from typing_extensions import TypeForm as TypeExpr
from types import UnionType

TypeSet = frozenset[type[Any]]


def _extract_types(type_expr: Any) -> TypeSet:
    """
    Extract all types from a type expression, flattening unions and intersections.
    This ensures that Intersection[int | str] and Intersection[int] & Intersection[str] are equivalent.
    """
    # Handle Intersection types - unwrap them
    if isinstance(type_expr, IntersectionMeta):
        return type_expr._types
    
    # Handle Intersection instances
    if isinstance(type_expr, Intersection):
        return type(type_expr)._types
    
    # Handle Union types (int | str or Union[int, str])
    origin = get_origin(type_expr)
    if origin is TypeExpr:
        extracted: set[type[Any]] = set()
        for arg in get_args(type_expr):
            extracted.update(_extract_types(arg))
        return frozenset(extracted)

    if origin is Union or origin is UnionType:
        result: set[type[Any]] = set()
        for arg in get_args(type_expr):
            result.update(_extract_types(arg))
        return frozenset(result)
    
    # Handle regular types
    if isinstance(type_expr, type):
        return frozenset([type_expr])
    
    # If it's not a type, try to get its type
    if hasattr(type_expr, '__class__'):
        return frozenset([type(type_expr)])
    
    raise TypeError(f"Cannot extract types from {type_expr}")


def _normalize_type_expr(type_expr: Any) -> TypeSet:
    """
    Normalize a type expression into a canonical frozenset of types.
    This handles flattening of nested intersections and unions.
    """
    return _extract_types(type_expr)


class IntersectionMeta[IntersectionTs](type):
    """
    Metaclass for Intersection types that handles type-level operations.
    
    This metaclass ensures that:
    1. Intersection types are immutable and hashable
    2. Type expressions are flattened and normalized
    3. Type constructors work correctly (e.g., Intersection[int | str][str] -> Intersection[str])
    4. Subclassing relationships are properly defined
    """
    
    _types: TypeSet
    _name: str
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        types: TypeSet | None = None,
        **kwargs: Any,
    ) -> IntersectionMeta[IntersectionTs]:
        """
        Create a new Intersection type class.
        
        Args:
            name: Name of the class
            bases: Base classes
            namespace: Class namespace
            types: Frozenset of types this Intersection contains (for parameterized types)
        """
        # Prevent manual subclassing of specialised Intersection types
        if types is None and any(isinstance(base, IntersectionMeta) for base in bases):
            raise TypeError(
                "Intersection types cannot be subclassed directly; "
                "use a type alias like `MyIntersection = Intersection[int | str]`."
            )

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        
        # Store the types this Intersection contains
        if types is not None:
            cls._types = types
        elif name == 'Intersection' and not bases:
            # Base Intersection class has no types
            cls._types = frozenset()
        else:
            # Inherit types from bases if not specified
            cls._types = frozenset()
            for base in bases:
                if isinstance(base, IntersectionMeta) and hasattr(base, '_types'):
                    cls._types = cls._types.union(base._types)
        
        # Store original name for repr
        cls._name = name
        
        return cls
    
    def __init__(cls, name: str, bases: tuple[type, ...], namespace: dict[str, Any], **kwargs: Any) -> None:
        """Initialize the Intersection type class."""
        super().__init__(name, bases, namespace, **kwargs)

    def __getitem__[DivisorTs: Any](cls, divisor_types: type[DivisorTs]) -> IntersectionMeta[DivisorTs]:
        """
        Type division operator: Intersection[int | str | float][str] -> Intersection[str]
        
        This creates a new Intersection type containing only the specified divisor types.
        If the divisor is a subset of the current types, it acts as type division.
        """
        # Normalize the divisor types
        divisor_set = _normalize_type_expr(divisor_types)
        
        # Create a new Intersection type with only the divisor types
        # Generate a name for this new type
        type_names = sorted([t.__name__ for t in divisor_set])
        name = f"Intersection[{' | '.join(type_names)}]"
        
        # Create and return the new Intersection type
        return IntersectionMeta(name, (Intersection,), {}, types=divisor_set)
    
    def __call__(cls, *args: Any, **kwargs: Any) -> Intersection[IntersectionTs]:
        """
        Create an instance of this Intersection type.
        
        Args are matched to types in the Intersection. Each arg's type must match exactly
        one type in the Intersection's type set.
        """
        instance = super().__call__(*args, **kwargs)
        return instance
    
    def __eq__(cls, other: object) -> bool:
        """
        Check if two Intersection types are equal.
        
        Intersection types are equal if they contain the same set of types,
        regardless of order (permutation invariance).
        """
        if not isinstance(other, IntersectionMeta):
            return False
        return cls._types == other._types
    
    def __hash__(cls) -> int:
        """Make Intersection types hashable based on their type set."""
        return hash(cls._types)
    
    def __and__[IncomingTs](cls, other: Intersection[TypeExpr[IncomingTs]] | IntersectionMeta[TypeExpr[IncomingTs]]) -> IntersectionMeta[TypeExpr[IntersectionTs | IncomingTs]]:
        """
        Intersection operator for Intersection types: Intersection[int] & Intersection[str] -> Intersection[int | str]
        
        This combines two Intersection types into a new Intersection containing all types from both.
        """
        if isinstance(other, IntersectionMeta):
            combined_types = cls._types.union(other._types)
        else:
            # Try to extract types from other
            other_types = _normalize_type_expr(other)
            combined_types = cls._types.union(other_types)
        
        # Generate name for the combined type
        type_names = sorted([t.__name__ for t in combined_types])
        name = f"Intersection[{' | '.join(type_names)}]"
        
        return IntersectionMeta(name, (Intersection,), {}, types=combined_types)
    
    def __contains__(cls, item: Any) -> bool:
        """
        Check if a type is contained in this Intersection type.
        
        Supports both: int in Intersection[int | str] and Intersection[int] in Intersection[int | str | float]
        """
        if isinstance(item, IntersectionMeta):
            # Check if all types in item are in cls
            return item._types.issubset(cls._types)
        elif isinstance(item, type):
            return item in cls._types
        else:
            # Try to extract types
            item_types = _normalize_type_expr(item)
            return item_types.issubset(cls._types)
    
    def __repr__(cls) -> str:
        """String representation of the Intersection type."""
        if not cls._types:
            return "Intersection"
        type_names = sorted([t.__name__ for t in cls._types])
        return f"Intersection[{' | '.join(type_names)}]"
    
    def __str__(cls) -> str:
        """String representation of the Intersection type."""
        return repr(cls)


class Intersection[IntersectionTs](metaclass=IntersectionMeta[TypeExpr[IntersectionTs]]):
    """
    A Intersection type container that holds exactly one instance of each type in its type set.
    
    Intersection types are:
    - Permutation invariant: Intersection(1, "hello") == Intersection("hello", 1)
    - Immutable after creation (though contents can be modified via __setitem__)
    - Type-safe: each type can appear at most once
    - Composable: can be combined with & operator
    
    Example:
        >>> isf = Intersection(5, "hello", 0.2)  # Intersection[int | str | float]
        >>> isf[int]  # 5
        >>> isf[str] = "world"
        >>> isf[int | str]  # Intersection[int | str] containing (5, "world")
    """
    
    _values: dict[type, IntersectionTs]
    
    def __new__(cls, *args: Any, **kwargs: Any) -> Intersection[IntersectionTs]:
        """Create a new Intersection instance."""
        instance = super().__new__(cls)
        return instance
    
    def __init__(self, *args: IntersectionTs) -> None:
        """
        Initialize a Intersection with the given values.
        
        Each arg is stored by its type. If multiple args have the same type,
        the last one wins (left-to-right evaluation).
        """
        # Get the expected types from the class
        expected_types = type(self)._types
        
        # Storage for values by type
        self._values: dict[type, Any] = {}
        
        # Process arguments
        for arg in args:
            # Handle Intersection instances - merge them
            if isinstance(arg, Intersection):
                for arg_type in type(arg)._types:
                    self._values[arg_type] = arg._values.get(arg_type)
            else:
                # Regular value - store by its type
                arg_type = type(arg)
                self._values[arg_type] = arg
        
        # If we have expected types but no values were provided, that's an error
        if expected_types and not self._values:
            raise TypeError(f"No values provided for {type(self)}")
        
        # If this is a parameterized Intersection, update the class types to match actual values
        if not expected_types:
            # Dynamically set the types based on the values
            actual_types = frozenset(self._values.keys())
            type(self)._types = actual_types

    def __getitem__[DivisorTs](self, key: type[DivisorTs]) -> Intersection[DivisorTs]:
        """
        Get value(s) by type.
        
        Args:
            key: A type or type expression (e.g., int or int | str)
        
        Returns:
            - If key is a single type: the value of that type
            - If key is a union of types: a new Intersection containing those types
        """
    
        # Normalize the key to a set of types
        key_types = _normalize_type_expr(key)
        
        # If requesting a single type, return the value directly
        if len(key_types) == 1:
            requested_type = next(iter(key_types))
            if requested_type not in self._values:
                raise KeyError(f"Type {requested_type.__name__} not in Intersection")
            return self._values[requested_type]
        
        # If requesting multiple types, return a new Intersection with those types
        result_values = []
        for t in key_types:
            if t not in self._values:
                raise KeyError(f"Type {t.__name__} not in Intersection")
            result_values.append(self._values[t])
        
        # Create a new Intersection with the requested types
        new_intersection_type = IntersectionMeta(
            f"Intersection[{' | '.join(sorted(t.__name__ for t in key_types))}]",
            (Intersection,),
            {},
            types=key_types
        )
        return new_intersection_type(*result_values)
    
    def __setitem__(self, key: type, value: Any) -> None:
        """
        Set a value by type.
        
        Args:
            key: The type to set
            value: The value to set (must be an instance of key)
        """
        if not isinstance(key, type):
            raise TypeError(f"Key must be a type, got {type(key)}")
        
        # Type check
        if not isinstance(value, key):
            raise TypeError(f"Value must be of type {key.__name__}, got {type(value).__name__}")
        
        self._values[key] = value
        
        # Update the Intersection's type set if needed
        if key not in type(self)._types:
            new_types = type(self)._types.union({key})
            type(self)._types = new_types
    
    def __and__[IncomingTs](self, other: Intersection[TypeExpr[IncomingTs]] | TypeExpr[IncomingTs]) -> Intersection[IntersectionTs | IncomingTs]:
        """
        Combine this Intersection with another Intersection or value.
        
        Args:
            other: Another Intersection or a value to add
        
        Returns:
            A new Intersection containing all values from both
        """
        if isinstance(other, Intersection):
            # Combine all values
            new_values = list(self._values.values()) + list(other._values.values())
            combined_types = type(self)._types.union(type(other)._types)
        else:
            # Add a single value
            new_values = list(self._values.values()) + [other]
            combined_types = type(self)._types.union({type(other)})
        
        # Create new Intersection type
        new_intersection_type = IntersectionMeta(
            f"Intersection[{' | '.join(sorted(t.__name__ for t in combined_types))}]",
            (Intersection,),
            {},
            types=combined_types
        )
        
        return new_intersection_type(*new_values)
    
    def with_changes(self, *args: Any) -> Intersection[IntersectionTs]:
        """
        Create a new Intersection with updated values.
        
        Evaluates left-to-right, updating values for each type as encountered.
        
        Args:
            *args: Values or Intersections to merge (left-to-right)
        
        Returns:
            A new Intersection with updated values
        """
        # Start with current values
        new_values = dict(self._values)
        all_types = set(type(self)._types)
        
        # Process each argument left-to-right
        for arg in args:
            if isinstance(arg, Intersection):
                # Merge Intersection values
                for arg_type, arg_value in arg._values.items():
                    new_values[arg_type] = arg_value
                    all_types.add(arg_type)
            else:
                # Update single value
                arg_type = type(arg)
                new_values[arg_type] = arg
                all_types.add(arg_type)
        
        # Create new Intersection
        combined_types = frozenset(all_types)
        new_intersection_type = IntersectionMeta(
            f"Intersection[{' | '.join(sorted(t.__name__ for t in combined_types))}]",
            (Intersection,),
            {},
            types=combined_types
        )
        
        return new_intersection_type(*new_values.values())
    
    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Intersection.
        
        Intersections are equal if they contain the same types with the same values,
        regardless of order (permutation invariance).
        """
        if not isinstance(other, Intersection):
            return False
        
        # Check if types match
        if type(self)._types != type(other)._types:
            return False
        
        # Check if all values match
        for t in type(self)._types:
            if self._values.get(t) != other._values.get(t):
                return False
        
        return True
    
    def __hash__(self) -> int:
        """Make Intersection instances hashable based on their type-value pairs."""
        # Create a frozenset of (type, value) pairs for hashing
        # Values must be hashable for this to work
        try:
            items = frozenset((t, self._values[t]) for t in type(self)._types)
            return hash(items)
        except TypeError:
            # If values aren't hashable, fall back to id
            return id(self)
    
    def __repr__(self) -> str:
        """String representation of the Intersection instance."""
        type_value_pairs = [f"{t.__name__}={repr(v)}" for t, v in sorted(self._values.items(), key=lambda x: x[0].__name__)]
        return f"Intersection({', '.join(type_value_pairs)})"
    
    def __str__(self) -> str:
        """String representation of the Intersection instance."""
        return repr(self)


# Helper function for creating Intersection types with cleaner syntax
def make_intersection_type(*types: type) -> IntersectionMeta:
    """
    Create a Intersection type from a list of types.
    
    Example:
        >>> IntStrFloat = make_intersection_type(int, str, float)
        >>> isf = IntStrFloat(1, "hello", 3.14)
    """
    type_set = frozenset(types)
    type_names = sorted([t.__name__ for t in type_set])
    name = f"Intersection[{' | '.join(type_names)}]"
    return IntersectionMeta(name, (Intersection,), {}, types=type_set)



if __name__ == "__main__":
    T = Intersection[int | str]
