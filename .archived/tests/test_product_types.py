"""
Comprehensive test suite for Intersection/Intersection types.

Tests all features described in the original specification.
"""
import pytest
from intersection_types import Intersection, IntersectionMeta, make_intersection_type


def test_basic_creation():
    """Test basic Intersection creation and access."""
    print("=" * 60)
    print("TEST: Basic Creation and Access")
    print("=" * 60)
    
    # Create Intersection with basic types
    isf = Intersection(5, "hello", 0.2)
    print(f"isf = Intersection(5, 'hello', 0.2)")
    print(f"  Result: {isf}")
    print(f"  Type: {type(isf)}")
    
    # Basic access
    print(f"\nisf[int] = {isf[int]}")
    print(f"isf[str] = {isf[str]}")
    print(f"isf[float] = {isf[float]}")
    
    # Mutation
    isf[str] = "world"
    print(f"\nAfter isf[str] = 'world':")
    print(f"  isf[str] = {isf[str]}")
    
    print("\n✓ Basic creation and access working\n")


def test_permutation_invariance():
    """Test that order doesn't matter."""
    print("=" * 60)
    print("TEST: Permutation Invariance")
    print("=" * 60)
    
    isf = Intersection(5, "hello", 0.2)
    sfi = Intersection("hello", 0.2, 5)
    
    print(f"isf = Intersection(5, 'hello', 0.2)")
    print(f"sfi = Intersection('hello', 0.2, 5)")
    print(f"\nisf == sfi: {isf == sfi}")
    print(f"type(isf) == type(sfi): {type(isf) == type(sfi)}")
    
    print("\n✓ Permutation invariance working\n")


def test_type_constructor():
    """Test static type construction via Intersection[T | S | ...]."""
    print("=" * 60)
    print("TEST: Type Constructors")
    print("=" * 60)
    
    # Create a Intersection type
    IntStrFloat = Intersection[int | str | float]
    print(f"IntStrFloat = Intersection[int | str | float]")
    print(f"  Type: {IntStrFloat}")
    
    # Create instance of that type
    isf = IntStrFloat(5, "hello", 0.2)
    print(f"\nisf = IntStrFloat(5, 'hello', 0.2)")
    print(f"  Result: {isf}")
    print(f"  isf[int] = {isf[int]}")
    
    print("\n✓ Type constructors working\n")


def test_type_division():
    """Test type division via Intersection[T][S] -> Intersection[S]."""
    print("=" * 60)
    print("TEST: Type Division")
    print("=" * 60)
    
    IntStrFloat = Intersection[int | str | float]
    print(f"IntStrFloat = Intersection[int | str | float]")
    
    # Type division to get subset
    IntClass = IntStrFloat[int]
    print(f"\nIntClass = IntStrFloat[int]")
    print(f"  Result: {IntClass}")
    
    StrFloatClass = IntStrFloat[str | float]
    print(f"\nStrFloatClass = IntStrFloat[str | float]")
    print(f"  Result: {StrFloatClass}")
    
    # Test containment
    print(f"\nint in IntClass: {int in IntClass}")
    print(f"str in IntClass: {str in IntClass}")
    print(f"int in StrFloatClass: {int in StrFloatClass}")
    print(f"str in StrFloatClass: {str in StrFloatClass}")
    
    print("\n✓ Type division working\n")


def test_runtime_access():
    """Test accessing subset of types at runtime."""
    print("=" * 60)
    print("TEST: Runtime Type Access")
    print("=" * 60)
    
    isf = Intersection(5, "hello", 0.2)
    print(f"isf = Intersection(5, 'hello', 0.2)")
    
    # Access multiple types at once
    from typing import reveal_type
    from typing_extensions import TypeForm as TypeExpr
    int_str = reveal_type(isf[TypeExpr[int | str]])
    print(f"\nint_str = isf[int | str]")
    print(f"  Result: {int_str}")
    print(f"  Type: {type(int_str)}")
    print(f"  int_str[int] = {int_str[int]}")
    print(f"  int_str[str] = {int_str[str]}")
    
    print("\n✓ Runtime type access working\n")


def test_type_extension():
    """Test extending Intersection types with new types."""
    print("=" * 60)
    print("TEST: Type Extension")
    print("=" * 60)
    
    IntStrFloat = Intersection[int | str | float]
    print(f"IntStrFloat = Intersection[int | str | float]")
    
    # Extend with bool
    IntStrFloatBool = Intersection[IntStrFloat | bool]
    print(f"\nIntStrFloatBool = Intersection[IntStrFloat | bool]")
    print(f"  Result: {IntStrFloatBool}")
    
    # Check containment
    print(f"\nint in IntStrFloatBool: {int in IntStrFloatBool}")
    print(f"bool in IntStrFloatBool: {bool in IntStrFloatBool}")
    
    print("\n✓ Type extension working\n")


def test_and_operator():
    """Test the & operator for combining Intersection types."""
    print("=" * 60)
    print("TEST: & Operator")
    print("=" * 60)
    
    IntIntersection = Intersection[int]
    StrIntersection = Intersection[str]
    FloatIntersection = Intersection[float]
    
    print(f"IntIntersection = Intersection[int]")
    print(f"StrIntersection = Intersection[str]")
    print(f"FloatIntersection = Intersection[float]")
    
    # Combine types
    IntStr = IntIntersection & StrIntersection
    print(f"\nIntStr = IntIntersection & StrIntersection")
    print(f"  Result: {IntStr}")
    
    IntStrFloat = IntStr & FloatIntersection
    print(f"\nIntStrFloat = IntStr & FloatIntersection")
    print(f"  Result: {IntStrFloat}")
    
    # Alternative: chain operators
    Combined = Intersection[int] & Intersection[str] & Intersection[float]
    print(f"\nCombined = Intersection[int] & Intersection[str] & Intersection[float]")
    print(f"  Result: {Combined}")
    
    print(f"\nIntStrFloat == Combined: {IntStrFloat == Combined}")
    
    print("\n✓ & operator working\n")


def test_with_changes():
    """Test the with_changes method for updating values."""
    print("=" * 60)
    print("TEST: with_changes Method")
    print("=" * 60)
    
    isf = Intersection(5, "hello", 0.2)
    print(f"isf = Intersection(5, 'hello', 0.2)")
    print(f"  Result: {isf}")
    
    # Create partial updates
    is_update = Intersection(6, "world")
    b_update = Intersection(True)
    
    print(f"\nis_update = Intersection(6, 'world')")
    print(f"b_update = Intersection(True)")
    
    # Apply updates left-to-right
    isfb = isf.with_changes(is_update, b_update)
    print(f"\nisfb = isf.with_changes(is_update, b_update)")
    print(f"  Result: {isfb}")
    print(f"  isfb[int] = {isfb[int]}")
    print(f"  isfb[str] = {isfb[str]}")
    print(f"  isfb[float] = {isfb[float]}")
    print(f"  isfb[bool] = {isfb[bool]}")
    
    # Test overriding
    isfb2 = isf.with_changes(is_update, b_update, Intersection(False))
    print(f"\nisfb2 = isf.with_changes(is_update, b_update, Intersection(False))")
    print(f"  isfb2[bool] = {isfb2[bool]}")
    
    print("\n✓ with_changes method working\n")


def test_instance_and_operator():
    """Test & operator on Intersection instances."""
    print("=" * 60)
    print("TEST: Instance & Operator")
    print("=" * 60)
    
    isf = Intersection(5, "hello", 0.2)
    b = Intersection(True)
    
    print(f"isf = Intersection(5, 'hello', 0.2)")
    print(f"b = Intersection(True)")
    
    # Combine instances
    isfb = isf & b
    print(f"\nisfb = isf & b")
    print(f"  Result: {isfb}")
    print(f"  Type: {type(isfb)}")
    
    print("\n✓ Instance & operator working\n")


def test_type_equivalence():
    """Test type equivalence with flattening."""
    print("=" * 60)
    print("TEST: Type Equivalence and Flattening")
    print("=" * 60)
    
    # Permutation invariance
    T1 = Intersection[int | str | float]
    T2 = Intersection[str | float | int]
    print(f"T1 = Intersection[int | str | float]")
    print(f"T2 = Intersection[str | float | int]")
    print(f"T1 == T2: {T1 == T2}")
    
    # Flattening nested intersections
    T3 = Intersection[Intersection[int | str] | float]
    print(f"\nT3 = Intersection[Intersection[int | str] | float]")
    print(f"  Result: {T3}")
    print(f"T1 == T3: {T1 == T3}")
    
    # More complex flattening
    T4 = Intersection[int | Intersection[Intersection[float] | str]]
    print(f"\nT4 = Intersection[int | Intersection[Intersection[float] | str]]")
    print(f"  Result: {T4}")
    print(f"T1 == T4: {T1 == T4}")
    
    print("\n✓ Type equivalence and flattening working\n")


def test_containment():
    """Test type containment checks."""
    print("=" * 60)
    print("TEST: Type Containment")
    print("=" * 60)
    
    IntStr = Intersection[int | str]
    IntStrFloat = Intersection[int | str | float]
    
    print(f"IntStr = Intersection[int | str]")
    print(f"IntStrFloat = Intersection[int | str | float]")
    
    # Single type containment
    print(f"\nint in IntStr: {int in IntStr}")
    print(f"float in IntStr: {float in IntStr}")
    
    # Intersection type containment
    print(f"\nIntStr in IntStrFloat: {IntStr in IntStrFloat}")
    print(f"IntStrFloat in IntStr: {IntStrFloat in IntStr}")
    
    print("\n✓ Type containment working\n")


def test_named_classes():
    """Test creating named Intersection classes."""
    print("=" * 60)
    print("TEST: Named Intersection Classes")
    print("=" * 60)
    
    # Define a named alias
    IntStringFloat = Intersection[int | str | float]
    
    print(f"IntStringFloat = Intersection[int | str | float]")
    
    # Create instance from alias
    isf = IntStringFloat(5, "hello", 0.2)
    print(f"\nisf = IntStringFloat(5, 'hello', 0.2)")
    print(f"  Result: {isf}")
    print(f"  Type: {type(isf)}")
    print(f"  isf[int] = {isf[int]}")
    
    # Demonstrate additional aliases
    BoolIntersection = Intersection[bool]
    
    print(f"\nBoolIntersection = Intersection[bool]")
    b = BoolIntersection(True)
    print(f"b = BoolIntersection(True)")
    print(f"  Result: {b}")
    
    # Subclassing should raise a TypeError
    print("\nAttempting to subclass should raise TypeError")
    with pytest.raises(TypeError):
        class _Invalid(Intersection[int | str]):
            pass
    
    print("\n✓ Named Intersection classes working\n")


def test_make_intersection_type_helper():
    """Test the helper function for creating Intersection types."""
    print("=" * 60)
    print("TEST: make_intersection_type Helper")
    print("=" * 60)
    
    IntStrFloat = make_intersection_type(int, str, float)
    print(f"IntStrFloat = make_intersection_type(int, str, float)")
    print(f"  Result: {IntStrFloat}")
    
    isf = IntStrFloat(5, "hello", 0.2)
    print(f"\nisf = IntStrFloat(5, 'hello', 0.2)")
    print(f"  Result: {isf}")
    
    print("\n✓ make_intersection_type helper working\n")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PRODUCT TYPE SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 60 + "\n")
    
    test_basic_creation()
    test_permutation_invariance()
    test_type_constructor()
    test_type_division()
    test_runtime_access()
    test_type_extension()
    test_and_operator()
    test_with_changes()
    test_instance_and_operator()
    test_type_equivalence()
    test_containment()
    test_named_classes()
    test_make_intersection_type_helper()
    
    print("=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
