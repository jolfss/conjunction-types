# Changelog

### v1.0.1
- Improved type annotations:
    - `ConjunctionMeta`'s `__and__`, `__rand__`, can now forward the current metaclass's union types.
    - `Conjunction`'s `__class_getitem__` and `__getitem__` can now forward incoming union types. 

### v1.0.0
First release.