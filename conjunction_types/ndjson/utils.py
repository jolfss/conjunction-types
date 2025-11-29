"""
NDJSON serialization utilities for Conjunction types.

Handles reading and writing Conjunction instances to NDJSON format for
incremental logging, resumption, and data documentation.

Supports generic types (e.g., list[int], dict[str, Any]) by serializing
the type representation and reconstructing it during deserialization.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator, Callable, TypeVar, get_origin
from types import GenericAlias

from conjunction_types import Conjunction

__all__ = [
    "ConjunctionSerializer",
    "NDJSONFile",
    "TypeRegistry",
    "mint",
]


T = TypeVar("T")


# NDJSON-specific serialization registry (extends core mint)
_ndjson_serializers: dict[Callable, Callable[[Any], Any]] = {}
"""Maps minted constructors to their custom serializers."""

_ndjson_deserializers: dict[str, Callable[[Any], Any]] = {}
"""Maps mint names to their custom deserializers."""


def mint(
    name: str,
    typ: type[T] | GenericAlias,
    serializer: Callable[[Any], Any] | None = None,
    deserializer: Callable[[Any], T] | None = None,
) -> Callable[..., T]:
    """
    Create a minted type constructor with optional NDJSON serialization support.

    This wraps the core mint() function and adds custom serialization/deserialization
    logic for NDJSON files.

    Args:
        name: Stable name for the type (used in JSON)
        typ: The type to mint (can be generic like list[int])
        serializer: Optional function to convert instances to JSON-serializable format
        deserializer: Optional function to reconstruct instances from JSON

    Returns:
        A callable constructor that creates tagged instances

    Example:
        >>> from conjunction_types.ndjson import mint, NDJSONFile
        >>> from conjunction_types import Conjunction
        >>>
        >>> # Basic minting for generic types
        >>> IntList = mint("IntList", list[int])
        >>> c = Conjunction(IntList([1, 2, 3]))
        >>>
        >>> # With custom serialization
        >>> class Point:
        ...     def __init__(self, x, y):
        ...         self.x = x
        ...         self.y = y
        >>>
        >>> PointType = mint(
        ...     "Point",
        ...     Point,
        ...     serializer=lambda p: {"x": p.x, "y": p.y},
        ...     deserializer=lambda d: Point(d["x"], d["y"])
        ... )
        >>>
        >>> file = NDJSONFile("data.ndjson")
        >>> file.append(Conjunction(PointType(10, 20)))
    """
    # Use core mint to create the constructor
    from conjunction_types import mint as core_mint

    constructor = core_mint(name, typ)

    # Register NDJSON-specific serialization if provided
    if serializer is not None:
        _ndjson_serializers[constructor] = serializer
    if deserializer is not None:
        _ndjson_deserializers[name] = deserializer

    return constructor


def _serialize_type(typ: type | GenericAlias) -> str:
    """
    Serialize a type (including generics) to a string representation.

    Checks minted types first for stable names.

    Examples:
        int -> "int"
        list[int] -> "list[int]"
        dict[str, list[int]] -> "dict[str, list[int]]"
        mint("MyList", list[int]) -> "MyList"
    """
    # Check if this type was minted (typ might be a minted constructor)
    from conjunction_types import get_mint_name

    mint_name = get_mint_name(typ) if callable(typ) else None
    if mint_name is not None:
        return mint_name

    # For GenericAlias (e.g., list[int]), repr() works fine
    if isinstance(typ, GenericAlias):
        return repr(typ)

    # For regular types, use __name__ for built-ins, __module__.__qualname__ for others
    if isinstance(typ, type):
        # Built-in types
        if typ.__module__ == 'builtins':
            return typ.__name__
        # Types from typing module or other modules
        elif hasattr(typ, '__module__') and hasattr(typ, '__qualname__'):
            return f"{typ.__module__}.{typ.__qualname__}"
        else:
            return typ.__name__

    # Fallback
    return repr(typ)


def _deserialize_type(type_repr: str, safe_globals: dict[str, Any] | None = None) -> type | GenericAlias:
    """
    Deserialize a type from its string representation.

    Checks minted types first for registered names.

    Args:
        type_repr: String representation of the type
        safe_globals: Optional dict of allowed names for eval

    Returns:
        The reconstructed type
    """
    # Check if this is a minted type name
    from conjunction_types import get_constructor_by_name

    constructor = get_constructor_by_name(type_repr)
    if constructor is not None:
        return constructor

    # Build a safe namespace for eval
    if safe_globals is None:
        safe_globals = {}

    # Add common typing constructs
    from typing import Any, Optional, Union
    import pathlib

    safe_namespace = {
        # Built-in types
        'int': int,
        'str': str,
        'float': float,
        'bool': bool,
        'bytes': bytes,
        'list': list,
        'dict': dict,
        'set': set,
        'tuple': tuple,
        'frozenset': frozenset,
        # Typing constructs
        'Any': Any,
        'Optional': Optional,
        'Union': Union,
        # Common stdlib modules
        'pathlib': pathlib,
        'Path': Path,
        # User-provided globals
        **safe_globals,
    }

    try:
        result = eval(type_repr, {"__builtins__": {}}, safe_namespace)
        return result
    except Exception as e:
        raise ValueError(f"Cannot deserialize type from repr: {type_repr}. Error: {e}")


class TypeRegistry:
    """
    Registry for custom type serializers and deserializers.

    Allows registering custom serialization logic for types that aren't
    directly JSON-serializable.
    """

    def __init__(self) -> None:
        self._serializers: dict[type, Callable[[Any], Any]] = {}
        self._deserializers: dict[str, Callable[[Any], Any]] = {}
        self._type_aliases: dict[str, type] = {}
        self._safe_globals: dict[str, Any] = {}

    def register(
        self,
        typ: type[T],
        serializer: Callable[[T], Any],
        deserializer: Callable[[Any], T],
        name: str | None = None,
    ) -> None:
        """
        Register a type with custom serialization logic.

        Args:
            typ: The type to register
            serializer: Function to convert instances to JSON-serializable format
            deserializer: Function to reconstruct instances from JSON
            name: Optional custom name for the type (defaults to typ.__name__)
        """
        type_name = name or typ.__name__
        self._serializers[typ] = serializer
        self._deserializers[type_name] = deserializer
        self._type_aliases[type_name] = typ
        # Add to safe globals for type deserialization
        self._safe_globals[type_name] = typ

    def register_type(self, name: str, typ: type) -> None:
        """
        Register a type for deserialization without custom serialization.

        Useful for making custom types available in the eval namespace.
        """
        self._type_aliases[name] = typ
        self._safe_globals[name] = typ

    def serialize_value(self, value: Any, value_type: type | GenericAlias) -> Any:
        """
        Serialize a value to JSON-compatible format.

        Checks minted serializers first, then registry serializers.

        Args:
            value: The value to serialize
            value_type: The type key from the Conjunction

        Returns:
            JSON-serializable representation of the value
        """
        # Check global NDJSON minted serializers first
        if value_type in _ndjson_serializers:
            return _ndjson_serializers[value_type](value)

        # Get the origin type for generic aliases (list[int] -> list)
        origin = get_origin(value_type)
        check_type = origin if origin is not None else value_type

        # Check for exact match serializer
        if value_type in self._serializers:
            return self._serializers[value_type](value)

        # Check for base type serializer
        if check_type in self._serializers:
            return self._serializers[check_type](value)

        # Check if value's runtime type has a serializer
        runtime_type = type(value)
        for registered_type, serializer in self._serializers.items():
            if isinstance(value, registered_type):
                return serializer(value)

        # Try to serialize directly for JSON-compatible types
        try:
            json.dumps(value)
            return value
        except (TypeError, ValueError):
            raise TypeError(
                f"Type {runtime_type} is not JSON-serializable. "
                f"Register a custom serializer using TypeRegistry.register() or mint()"
            )

    def deserialize_value(self, data: Any, value_type: type | GenericAlias) -> Any:
        """
        Deserialize a value from JSON format.

        Checks minted deserializers first, then registry deserializers.

        Args:
            data: The serialized value
            value_type: The type to reconstruct

        Returns:
            Reconstructed value
        """
        # Check global NDJSON minted deserializers first
        # Check if value_type is a minted constructor
        from conjunction_types import get_mint_name

        mint_name = get_mint_name(value_type) if callable(value_type) else None
        if mint_name is not None and mint_name in _ndjson_deserializers:
            return _ndjson_deserializers[mint_name](data)

        # Check if we have a custom deserializer for this type
        type_name = getattr(value_type, '__name__', None)

        if type_name and type_name in self._deserializers:
            return self._deserializers[type_name](data)

        # For generic types, get the origin
        origin = get_origin(value_type)
        if origin is not None:
            # For generics like list[int], just construct using the origin
            origin_name = origin.__name__
            if origin_name in self._deserializers:
                return self._deserializers[origin_name](data)
            # Default: use the origin type constructor
            return origin(data) if data is not None else None

        # For regular types, try direct construction
        if isinstance(value_type, type):
            if type_name and type_name in self._deserializers:
                return self._deserializers[type_name](data)
            return value_type(data) if data is not None else None

        # Fallback: return the data as-is
        return data


# Global default registry
_default_registry = TypeRegistry()


class ConjunctionSerializer:
    """Serialize/deserialize Conjunction instances to/from JSON."""

    def __init__(self, registry: TypeRegistry | None = None) -> None:
        """
        Initialize serializer with optional custom type registry.

        Args:
            registry: Custom type registry. If None, uses global default.
        """
        self.registry = registry or _default_registry

    def to_json(self, conj: Conjunction) -> dict[str, Any]:
        """
        Serialize a Conjunction to JSON-compatible dict.

        Serializes the actual type keys from the Conjunction, preserving
        generic types like list[int], dict[str, Any], etc.

        Returns a dict with type representations:
            {
                "__conjunction_types__": [
                    {"type": "int", "key": "int_0"},
                    {"type": "str", "key": "str_0"},
                    {"type": "list[int]", "key": "list_0"}
                ],
                "int_0": 42,
                "str_0": "hello",
                "list_0": [1, 2, 3]
            }
        """
        result: dict[str, Any] = {
            "__conjunction_types__": []
        }

        # Track counts for each base type name to handle duplicates
        type_counts: dict[str, int] = {}

        # Iterate through actual type keys in the Conjunction
        for typ in conj._data.keys():
            # Serialize the type
            type_repr = _serialize_type(typ)

            # Generate a unique key for this value
            # Use the base name (int, list, etc.) with a counter
            base_name = getattr(typ, '__name__', None)
            if base_name is None:
                # For generic aliases, get the origin's name
                origin = get_origin(typ)
                base_name = origin.__name__ if origin else 'type'

            count = type_counts.get(base_name, 0)
            value_key = f"{base_name}_{count}"
            type_counts[base_name] = count + 1

            # Store type metadata
            result["__conjunction_types__"].append({
                "type": type_repr,
                "key": value_key
            })

            # Serialize the value
            value = conj._data[typ]
            serialized_value = self.registry.serialize_value(value, typ)
            result[value_key] = serialized_value

        return result

    def from_json(self, data: dict[str, Any]) -> Conjunction:
        """
        Deserialize a Conjunction from JSON.

        Args:
            data: JSON dict with "__conjunction_types__" metadata

        Returns:
            Reconstructed Conjunction with proper type keys
        """
        if "__conjunction_types__" not in data:
            raise ValueError("Missing '__conjunction_types__' key in JSON data")

        type_metadata = data["__conjunction_types__"]

        if not type_metadata:
            raise ValueError("Cannot create empty Conjunction")

        # Build the Conjunction by reconstructing its internal data
        result = Conjunction.__new__(Conjunction)
        conj_data = {}

        for entry in type_metadata:
            type_repr = entry["type"]
            value_key = entry["key"]

            if value_key not in data:
                raise ValueError(f"Missing value for key: {value_key}")

            # Deserialize the type
            typ = _deserialize_type(type_repr, self.registry._safe_globals)

            # Deserialize the value
            serialized_value = data[value_key]
            value = self.registry.deserialize_value(serialized_value, typ)

            conj_data[typ] = value

        # Set internal state
        object.__setattr__(result, '_data', conj_data)
        object.__setattr__(result, '_hash', None)

        return result


class NDJSONFile:
    """Utilities for reading/writing NDJSON files with Conjunction instances."""

    def __init__(
        self,
        path: Path | str,
        registry: TypeRegistry | None = None,
    ) -> None:
        """
        Initialize NDJSON file handler.

        Args:
            path: Path to NDJSON file
            registry: Custom type registry for serialization
        """
        self.path = Path(path)
        self.serializer = ConjunctionSerializer(registry)

    def append(self, conj: Conjunction) -> None:
        """Append a Conjunction to the NDJSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = self.serializer.to_json(conj)

        with open(self.path, 'a') as f:
            f.write(json.dumps(data) + '\n')

    def read(self) -> Iterator[Conjunction]:
        """
        Read Conjunction instances from NDJSON file line by line.

        Yields:
            Conjunction instances, one per line
        """
        if not self.path.exists():
            return

        with open(self.path) as f:
            for line in f:
                if line.strip():  # Skip empty lines
                    data = json.loads(line)
                    yield self.serializer.from_json(data)

    def read_raw(self) -> Iterator[dict[str, Any]]:
        """
        Read raw JSON dicts from NDJSON file.

        Yields:
            Raw dict objects without deserialization
        """
        if not self.path.exists():
            return

        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def count_lines(self) -> int:
        """Count number of lines in NDJSON file."""
        if not self.path.exists():
            return 0

        with open(self.path) as f:
            return sum(1 for line in f if line.strip())

    def write_all(self, conjunctions: list[Conjunction]) -> None:
        """
        Write multiple Conjunctions to NDJSON file (overwrites existing).

        Args:
            conjunctions: List of Conjunction instances to write
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.path, 'w') as f:
            for conj in conjunctions:
                data = self.serializer.to_json(conj)
                f.write(json.dumps(data) + '\n')
