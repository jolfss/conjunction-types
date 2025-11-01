"""
An implementation of Product/Intersection types; this naturally encapsulates the pattern of a pipeline
and introduces a form of dependent typing to Python. Inspiration is drawn from conversations with other
teams about how they structure their code bases.

This version uses TypeForm (Python 3.13+) for cleaner type hints.
"""
from __future__ import annotations
import sys
from typing import Any, Protocol, Mapping, cast, runtime_checkable, get_args, Union, TypeVar, overload
import warnings
from dataclasses import dataclass
import re
import types

from typing_extensions import TypeForm  # Will be available in Python 3.15, PEP 747


def pascal_to_snake(s: str) -> str:
    """Convert MyTypeName -> my_type_name"""
    # Insert underscore before uppercase letters that follow lowercase letters
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    # Insert underscore before uppercase letters that follow lowercase or uppercase followed by lowercase
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    return s.lower()


class ProductMeta[ProductTs : TypeForm[Any]](type):
    """Metaclass that extracts union types and creates unordered generic semantics."""
    
    def __call__(cls, *args, **kwargs) -> Product[ProductTs]:
        """
        Handle instance creation, allowing both Product[T](...) and Subclass(...) patterns.
        """
        # Use type's __call__ to handle the normal instantiation process
        return type.__call__(cls, *args, **kwargs)


    def __getitem__[DivisorTs : TypeForm[Any]](cls, divisor_types : TypeForm[DivisorTs]) -> ProductMeta[DivisorTs]:
        """
        Called when you write Product[SubItem1 | SubItem2 | SubItem3]
        Returns a new class with the union types stored.
        """
        # Extract types from the union
        # Handle both typing.Union and types.UnionType (Python 3.10+)
        if isinstance(divisor_types, types.UnionType) or (hasattr(divisor_types, '__origin__') and divisor_types.__origin__ is Union):
            sub_types = get_args(divisor_types)
        else:
            # Single type, not a union
            sub_types = (divisor_types,)
        
        # Normalize to a frozenset for unordered comparison
        sub_types_set = frozenset(sub_types)
        
        # Create a new class that remembers its sub-types
        class_name = f"{cls.__name__}[{' | '.join(t.__name__ for t in sub_types)}]"
        
        # Check if we've already created this exact type combination
        cache_key = (cls, sub_types_set)
        if hasattr(cls, '_generic_cache'):
            if cache_key in cls._generic_cache:
                return cls._generic_cache[cache_key]
        else:
            cls._generic_cache = {}
        
        # Create new class with the sub-types stored
        new_cls = type.__new__(
            ProductMeta,
            class_name,
            (cls,),
            {
                '__sub_types__': sub_types_set,
                '__sub_types_list__': sub_types,  # Keep order for convenience
            }
        )
        
        cls._generic_cache[cache_key] = new_cls
        return new_cls
    
    def __eq__(cls, other):
        """Item[str | int] == Item[int | str]"""
        if not isinstance(other, ProductMeta):
            return False
        
        # Get base classes
        cls_base = cls if not hasattr(cls, '__sub_types__') else cls.__bases__[0]
        other_base = other if not hasattr(other, '__sub_types__') else other.__bases__[0]
        
        # Use identity comparison to avoid recursion
        if id(cls_base) != id(other_base):
            return False
        
        # Compare sub-types as sets
        cls_types = getattr(cls, '__sub_types__', frozenset())
        other_types = getattr(other, '__sub_types__', frozenset())
        
        return cls_types == other_types
    
    def __hash__(cls):
        """Make the class hashable based on its sub-types."""
        cls_base = cls if not hasattr(cls, '__sub_types__') else cls.__bases__[0]
        sub_types = getattr(cls, '__sub_types__', frozenset())
        # Use id() to avoid recursion when hashing the base class
        return hash((id(cls_base), sub_types))
    
    def __instancecheck__(cls, instance):
        """
        Support isinstance(val, Product[int | str]) checks.
        Checks if the instance contains all the required types.
        """
        # Avoid recursion by checking the type directly
        if not (hasattr(instance, '_typemap') and type(instance).__mro__[0].__name__ == 'Product' or 
                any(base.__name__ == 'Product' for base in type(instance).__mro__)):
            return False
        
        # Get the types this class requires
        required_types = getattr(cls, '__sub_types__', frozenset())
        if not required_types:
            # Non-generic Product, just check if it's a Product
            return True
        
        # Flatten any nested Product types
        flattened_required = Product._flatten_product_types(required_types)
        
        # Get the types available in the instance
        available_types = set(instance._typemap.keys())
        
        # Check if all required types are present
        return flattened_required.issubset(available_types)



class Product[ItemTs : TypeForm[Any]](metaclass=ProductMeta):
    """The implementation of generically-supported product types."""
    
    # Type hint for the _typemap attribute
    _typemap: Mapping[type, Any]
    
    @classmethod
    def get_validated_typemap(cls, **items: ItemTs) -> Mapping[type[ItemTs], ItemTs]:
        """
        Validate that provided items match the declared types.
        Now accepts keyword arguments instead of positional.

        Actual return type bound is narrower than can be expressed:
            `Mapping[type[T : in ItemTs], T]`
        """
        _proto_typemap = {}
        
        # Get expected types from the class
        expected_types = getattr(cls, '__sub_types__', frozenset())
        
        for key, item in items.items():
            _ItemT = type(item)
            
            if expected_types and _ItemT not in expected_types:
                warnings.warn(f"{item} (type {_ItemT.__name__}) was not declared in the parent item's generics")
            
            if _ItemT in _proto_typemap:
                warnings.warn(f"Type {_ItemT.__name__} was *already* included, only most recent argument will be captured")
            
            _proto_typemap[_ItemT] = item
        
        return _proto_typemap
    
    def __init__(self, *args, **items):
        """
        Initialize with positional arguments (typed by their actual types) 
        or keyword arguments for each subitem.
        Keys can be snake_case versions of type names or custom names.
        """
        # Handle positional arguments
        if args:
            # Build typemap directly from positional arguments
            _proto_typemap = {}
            expected_types = getattr(self.__class__, '__sub_types__', frozenset())
            
            for arg in args:
                arg_type = type(arg)
                
                if expected_types and arg_type not in expected_types:
                    warnings.warn(f"{arg} (type {arg_type.__name__}) was not declared in the parent item's generics")
                
                if arg_type in _proto_typemap:
                    warnings.warn(f"Type {arg_type.__name__} was *already* included, only most recent argument will be captured")
                
                _proto_typemap[arg_type] = arg
            
            # Handle any keyword arguments by matching them to types
            for key, value in items.items():
                value_type = type(value)
                if value_type in _proto_typemap:
                    warnings.warn(f"Type {value_type.__name__} was *already* included, keyword argument will override")
                _proto_typemap[value_type] = value
            
            self._typemap = _proto_typemap
        
        # Handle keyword-only arguments
        elif items:
            # Try to match keyword arguments to types
            matched_items = {}
            expected_types = getattr(self.__class__, '__sub_types__', frozenset())
            
            # Create a mapping from snake_case names to types
            type_name_map = {pascal_to_snake(t.__name__): t for t in expected_types}
            
            for key, value in items.items():
                value_type = type(value)
                
                # Direct type match
                if value_type in expected_types:
                    matched_items[key] = value
                # Try matching by name
                elif key in type_name_map:
                    matched_items[key] = value
                else:
                    matched_items[key] = value
            
            self._typemap = self.get_validated_typemap(**matched_items)
        
        # Empty initialization for subclasses
        elif not hasattr(self, '_typemap'):
            self._typemap = {}
    
    def __new__(cls, *args, **kwargs) -> Product[ItemTs]:
        """Type hint ensures Product[int | str](...) returns Product[int | str]."""
        instance = super().__new__(cls)
        return instance
    
    def __getitem__[DivisorTs : TypeForm[Any]](self, item_type : DivisorTs) -> Product[DivisorTs]:
        """
        Get an item by its type, or perform type slicing.
        
        If item_type is a Product type with generics, this validates that all
        requested types exist in this instance and returns a sliced view.
        
        Examples:
            val[int] -> returns the int value
            val[Product[int | str]] -> returns Product instance with only int and str
        """
        # Check if this is a type slicing operation (Product[...] generic)
        if isinstance(item_type, ProductMeta) and hasattr(item_type, '__sub_types__'):
            # This is type slicing: val[Product[int | str]]
            requested_types = item_type.__sub_types__
            
            # Flatten any nested Product types in requested_types
            flattened_requested = self._flatten_product_types(requested_types)
            
            # Check if all requested types are present in this instance
            available_types = set(self._typemap.keys())
            
            if not flattened_requested.issubset(available_types):
                missing = flattened_requested - available_types
                missing_names = ', '.join(t.__name__ for t in missing)
                raise TypeError(f"Cannot slice: types {missing_names} not found in this Product instance")
            
            # Return a new Product instance with only the requested types
            filtered_items = {k: v for k, v in self._typemap.items() if k in flattened_requested}
            
            # Create a new instance with the filtered types
            new_instance = object.__new__(item_type)
            new_instance._typemap = filtered_items
            return new_instance
        
        # Regular type access: val[int]
        if item_type not in self._typemap:
            raise KeyError(f"Type {item_type.__name__} not found in this Item")
        return cast(item_type, self._typemap[item_type])
    
    @staticmethod
    def _flatten_product_types(types_set: frozenset) -> set:
        """
        Recursively flatten nested Product types.
        Product[Product[str|int] | float] -> {str, int, float}
        """
        result = set()
        for t in types_set:
            if isinstance(t, ProductMeta) and hasattr(t, '__sub_types__'):
                # Recursively flatten nested Product
                result.update(Product._flatten_product_types(t.__sub_types__))
            else:
                result.add(t)
        return result


if __name__ == "__main__":
    # Example usage:
    class SubItem1(Product):
        def __init__(self, value: str):
            self.value = value
            super().__init__()

    class SubItem2(Product):
        def __init__(self, value: int):
            self.value = value
            super().__init__()

    class SubItem3(Product):
        def __init__(self, value: float):
            self.value = value
            super().__init__()

    class SubItem4(Product):
        def __init__(self, value: bool):
            self.value = value
            super().__init__()


    # Now you can use it like this:
    class MyItem(Product[TypeForm[SubItem1 | SubItem2 | SubItem3]]):
        pass

    class MySlice(Product[TypeForm[SubItem1 | SubItem2]]):
        pass

    # Test that order doesn't matter:
    assert Product[TypeForm[SubItem1 | SubItem2]] == Product[TypeForm[SubItem2 | SubItem1]]
    print("✓ Order-independence works!")

    # Create instances:
    sub1 = SubItem1("hello")
    sub2 = SubItem2(42)
    sub3 = SubItem3(3.14)
    sub4 = SubItem4(True)

    my_item = MyItem(sub1, sub2, sub3)

    MyType = Product[TypeForm[SubItem1 | SubItem2]]
    my_item_cub = my_item[MySlice]
    my_item_cub = my_item[TypeForm[MyType]]

    # Access by type:
    retrieved_sub1 = my_item[SubItem1]
    print(f"✓ Retrieved SubItem1: {retrieved_sub1.value}")

    retrieved_sub2 = my_item[SubItem2]
    print(f"✓ Retrieved SubItem2: {retrieved_sub2.value}")

    # Test type inference
    retrieved_sub3 = my_item[SubItem3]
    print(f"✓ Retrieved SubItem3: {retrieved_sub3.value}")

    print("\n=== Testing Type Slicing ===")
    
    # Create a product with int, str, float
    val = Product[int | str | float](42, "hello", 3.14)
    
    # Type definitions
    T1 = Product[int | float | str | bool]  # Contains bool which val doesn't have
    T2 = Product[str | int]  # Subset of val
    
    # Test isinstance checks
    print("\nTesting isinstance checks:")
    assert not isinstance(val, T1), "val should not be instance of T1 (contains bool)"
    print("✓ isinstance(val, T1) == False (T1 requires bool)")
    
    assert isinstance(val, T2), "val should be instance of T2 (subset)"
    print("✓ isinstance(val, T2) == True (T2 is subset)")
    
    assert isinstance(val, Product[str | float]), "val should contain str and float"
    print("✓ isinstance(val, Product[str | float]) == True")
    
    # Test slicing
    print("\nTesting type slicing:")
    sliced = val[T2]
    assert isinstance(sliced, T2)
    print(f"✓ val[T2] succeeded, result has types: {set(t.__name__ for t in sliced._typemap.keys())}")
    
    # Verify sliced product contains correct types
    assert int in sliced._typemap
    assert str in sliced._typemap
    assert float not in sliced._typemap
    print("✓ Sliced product contains only requested types (int, str)")
    
    # Test nested slicing
    sliced2 = val[Product[str | float]]
    assert isinstance(sliced2, Product[str | float])
    print("✓ val[Product[str | float]] succeeded")
    
    # Test that val[T1] should fail (T1 requires bool which val doesn't have)
    print("\nTesting error cases:")
    try:
        val[T1]
        assert False, "Should have raised TypeError"
    except TypeError as e:
        print(f"✓ val[T1] correctly raised TypeError: {e}")
    
    # Test that val[Product[bool]] should fail
    try:
        val[Product[bool]]
        assert False, "Should have raised TypeError"
    except TypeError as e:
        print(f"✓ val[Product[bool]] correctly raised TypeError: {e}")
    
    # Test recursive Product types
    print("\nTesting recursive Product types:")
    NestedProduct = Product[Product[str | int] | float]
    val2 = Product[str | int | float](a="test", b=10, c=2.5)
    
    assert isinstance(val2, NestedProduct)
    print("✓ isinstance(val2, Product[Product[str|int] | float]) == True (flattening works)")
    
    sliced3 = val2[NestedProduct]
    assert str in sliced3._typemap
    assert int in sliced3._typemap
    assert float in sliced3._typemap
    print("✓ Recursive slicing works correctly")

    print("\n✓ All tests passed! Type slicing works correctly.")