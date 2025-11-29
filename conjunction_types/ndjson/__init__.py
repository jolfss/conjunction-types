"""
Optional NDJSON extension for conjunction-types.

This module provides utilities for serializing and deserializing Conjunction
instances to/from NDJSON (newline-delimited JSON) format.

Usage:
    from conjunction_types.ndjson import NDJSONFile, ConjunctionSerializer

    # Write Conjunctions to NDJSON
    file = NDJSONFile("data.ndjson")
    file.append(Conjunction(42, "hello", 3.14))
    file.append(Conjunction(100, "world", 2.71))

    # Read back
    for conj in file.read():
        print(conj.to(int), conj.to(str))

    # Custom type serialization
    from conjunction_types.ndjson import TypeRegistry
    from pathlib import Path

    registry = TypeRegistry()
    registry.register(
        Path,
        serializer=str,
        deserializer=Path,
    )

    file = NDJSONFile("paths.ndjson", registry=registry)
    file.append(Conjunction(Path("/tmp"), "config"))
"""

from .utils import (
    ConjunctionSerializer,
    NDJSONFile,
    TypeRegistry,
    mint,
)

__all__ = [
    "ConjunctionSerializer",
    "NDJSONFile",
    "TypeRegistry",
    "mint",
]
