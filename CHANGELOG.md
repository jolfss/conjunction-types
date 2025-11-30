# Changelog

### Unreleased
- Added `mint()` function to core `conjunction_types`:
    - Wraps `NewType` to attach full type information (e.g. generics) to the bound type.
    - Allows for types with the same structure to exist in the same Conjunction.
    - Use it to create ad hoc types 
    - Improved error messages when GenericAlias is used on a Conjunction.

- Added optional `ndjson` extension for serializing/deserializing Conjunction instances

### v1.0.1
- Improved type annotations:
    - `ConjunctionMeta`'s `__and__`, `__rand__`, can now forward the current metaclass's union types.
    - `Conjunction`'s `__class_getitem__` and `__getitem__` can now forward incoming union types. 

### v1.0.0
- First release.
