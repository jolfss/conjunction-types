"""
A limited implementation of Product/Intersection types in Python.

A `Product[T | S | ...]` is a container with a set of unordered types and exactly one instance of that type. This is only a product type in the sense that the subclassing relation holds, `Product[T|...] <: T`. 

Nested products are deliberately flattened. TODO: Explain this design decision; it's really important.

There is some irony in using the union operator for product types, but using '|' avoids (1) issues with TypeVarTuple, (2) enforces type-order invariance, (3) non-duplicity, (4) type resolution over type constructor operations and (5) staying syntactically elegant and fun to use.

For now, we can consider that the product type distributes over the sum, which is quite fitting. No unions can exist within product types. For types which have already been lifted into the Product type system, the '&' operator can be used. At some point in the future, someone smart will implement Product types across Python and we will be able to replace `Product[int | str | float]` with `int & str & float`. 


The closest analogy to product types in base Python is the `@dataclass`, whose woes with multiple inheritance are well known. 
```python
    # classes
    class IntStringFloat(Product[int | str | float]):
        ...
    class BoolClass(Product[bool]): 
        ...
    isf = IntStringFloat(5, "hello", 0.2)   # equiv. Product[int, str, float]
    sfi = Product("hello", 0.2, 5)
    isf == sfi                              # permutation invariance
    is = IntString(6,"world")
    b = BoolClass(True)
    isfb = isf.with_changes(is, b, ..., BoolClass(False))  # evaluates left-to-right; avoids multiple copy
    # isfb == IntStringFloatBool(6, "world", 0.2, False)

    # class access
    isf[int] == 5                               # basic access
    isf[str] = "world"                          # mutation
    isf[int | str] == _IntString(5, "hello")     # runtime type creation

    # static type constructors
    IntClass = IntStringFloat[str]                      # metaclass type constructor via type division
    StrFloatClass = IntStringFloat[str | int]           # type divisors
    StrFloatBoolClass = Product[IntStringFloat | bool]  # type extension; === Product[int | str | float | bool]
    # also equivalent to Product[int] & Product[str] & Product[float] & Product[bool]

    # type metaclass functions
    int in IntClass                         # True
    Product[str | int] in StrFloatBoolClass # True
    Product[str] & Product[int]             # Product[str | int]
    Product[str] | Product[int]             # Since it is *outside* any Product, this is truly a union
    Product[Product[str] | Product[int]]    # This is not a union, it is an & since it is inside a Product

    # equivalence
    Product[int | str | float] == Product[str | float | int]                            # permutation invariance
    Product[Product[int|str] & float] == Product[int | Product[Product[float] & str]]   # type flattening
    # Within a Product, the '|' operator functions like '&', so the above is still fine.
    # Unions aren't allowed within Product types, period.

    # subclassing
    Product[int | str] <: Product[int | str | ...]    # type division subclassing
```
"""
from typing import overload
from typing_extensions import TypeForm as TypeExpr

class ProductMeta[ProductTs: TypeExpr](type):
    """
    """
    #
    # product type constructors
    #
    def __new__(mcs, name, bases, namespace, **kwargs) -> ProductMeta[ProductTs]:
        raise NotImplementedError()

    def __init__(cls, name, bases, namespace, **kwargs):
        raise NotImplementedError()
    
    def __getitem__[DivisorTs : TypeExpr](cls, divisor_types : DivisorTs) -> ProductMeta[DivisorTs]:
        raise NotImplementedError()

    def __call__(cls, *args, **kwargs) -> ProductMeta[ProductTs]:
        raise NotImplementedError()
    
    #
    # implementation
    #
    def __eq__(self, value: object) -> bool:
        raise NotImplementedError()

    def __and__[IncomingTs: TypeExpr](self, value: Product[IncomingTs]) -> ProductMeta[ProductTs | IncomingTs]:
        raise NotImplementedError()
    
    ... # TODO: Rest of the dunders, etc.


class Product[ProductTs:TypeExpr](metaclass=ProductMeta):
    """
    """
    def __new__(cls, *args, **kwargs) -> Product[ProductTs]:
        raise NotImplementedError()

    def __init__(self, *args : ProductTs):
        raise NotImplementedError()
    
    def __getitem__[DivisorTs: TypeExpr](self, divisor_types: DivisorTs) -> Product[DivisorTs]:
        raise NotImplementedError()

    def __and__[IncomingTs: TypeExpr](self, value: IncomingTs) -> Product[ProductTs | IncomingTs]:
        raise NotImplementedError()
    
    ... # TODO: Rest of the dunders, etc.