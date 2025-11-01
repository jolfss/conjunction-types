"""
A limited implementation of Intersection types in Python.

A `Intersection[A|B|...]` is a container with a set of unordered types and, for each, an instance of said type. This implementation is faithful in the sense that any Intersection *can* satisfy the subtyping relation `Intersection[A|...] <: A` for all types in the Intersection IF the supertype is known. Manually, a larger set of intersection types can be supported by inspection.

Nested intersections are deliberately flattened to avoid nested intersection wrappers and maintain a single canonical form for any given set of types. This ensures that Intersection[Intersection[int | str] | float] == Intersection[int | str | float], which is essential for type comparison, subclassing relationships, and predictable behavior when using type constructors that produce Intersection types dynamically.

For now, we just try to imagine that the intersection type distributes over the sum '|', which is quite fitting in a way: `Intersection[A|B] => Intersection[A] & Intersection[B] => A & B`. As such, no unions can exist within intersection types. This is actually a good design since it guarantees subtyping based on the signature; if you want to implement unions, nesting them in a class is a better approach anyway, since it'd be cleaner to implement this handling there anyway. 

Also, as demonstrated, for types which have already been lifted into the Intersection type system, the '&' operator can be used among them.

The closest analogy to intersection types in base Python is the `@dataclass`, whose woes 
with multiple inheritance are well known. Even Intersection types per se have been a thorny topic in the Python community. [There's over a decade of work](https://github.com/python/typing/issues/18) since Intersection types were first posed. Since then, a [gargantuan issue on the typing github](https://github.com/python/typing/issues/213) has not made much progress. Recently, people noted [unintuitive behavior in TypeGuard](https://peps.python.org/pep-0742/) and so they created [TypeIs](https://peps.python.org/pep-0742/) in 3.13, which included some internal intersection and negation implementations. Unfortunately, these also seem to have [issues](https://discuss.python.org/t/better-specification-for-when-the-presence-of-typing-never-should-be-considered-a-type-system-error/89757/42) and violate some of the agreed-upon heuristics for gradual typing in Python. There are some [recent attempts to pose a draft](https://github.com/CarliJoy/intersection_examples/issues/53), but given the apparent difficulty.
"""

from intersection_types._core import (
    Intersection,
    IntersectionMeta,
    make_intersection_type,
)

__version__ = "0.1.0"
__all__ = [
    "Intersection",
    "IntersectionMeta",
    "make_intersection_type",
]
