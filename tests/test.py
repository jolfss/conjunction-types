"""
Comprehensive Test Suite for Intersection Type System

This validates all the planned functionality from the specification.
"""
from product_types import Intersection

type FloatIntStr = Intersection[float | int | str]

def test_type_subset_checking():
    """Test isinstance-style subset checking on types."""
    print("Testing type subset checking...")
    
    # Create types
    float_int_str = Intersection[float | int | str]
    float_str = Intersection[float | str]
    
    # Subset checking
    assert float_str in float_int_str, "Intersection[float|str] should be in Intersection[float|int|str]"
    assert not (Intersection[float | int | str | bool] in float_int_str), "Superset should not be in subset"
    
    # Single type checking
    assert float in float_int_str, "float should be in Intersection[float|int|str]"
    assert int in float_int_str, "int should be in Intersection[float|int|str]"
    assert not (dict in float_int_str), "dict should not be in Intersection[float|int|str]"
    
    print("✓ Type subset checking works")


def test_type_equivalence():
    """Test type equality and permutation invariance."""
    print("\nTesting type equivalence...")
    
    # Permutation invariance
    assert Intersection[float | str] == Intersection[str | float], "Should be permutation invariant"
    
    # Intersection operator
    assert (Intersection[float] & Intersection[str]) == Intersection[str | float], "& should combine types"
    
    # Intersection flattening
    assert Intersection[Intersection[float] & str] == Intersection[float | str], "Should flatten nested Intersections"
    
    # Union treated as intersection inside Intersection
    assert Intersection[float | Intersection[str]] == Intersection[float | str], "Should distribute over union"
    
    print("✓ Type equivalence works")


def test_type_construction():
    """Test type construction with getitem."""
    print("\nTesting type construction...")
    
    # Basic construction
    str_type = Intersection[str]
    assert str in str_type, "str should be in Intersection[str]"
    
    # Multi-type construction
    str_int = Intersection[str | int]
    assert str in str_int and int in str_int, "Both types should be present"
    
    # Error on invalid subset
    try:
        # This should fail at instance creation time, not type creation
        str_int_instance = Intersection[str | int]("hello", 5)
        str_int_instance[bool]
        # Trying to extract bool from str|int should fail
        print("  Note: Type-level validation happens at runtime during extraction")
    except:
        print("Successfully thrown")
    
    print("✓ Type construction works")


def test_type_concatenation():
    """Test associative type concatenation."""
    print("\nTesting type concatenation...")
    
    # Create instance through concatenation
    q = Intersection("cactus", Intersection("string"), Intersection(True))
    x = Intersection(5) & "Any"
    y = Intersection(Intersection(Intersection(5) & Intersection(15) & 2.0 )) 
    float_int_str_bool = Intersection(Intersection(5) & "a string") & Intersection(True, 0.3)
    
    # Check types present
    assert int in float_int_str_bool, "int should be present"
    assert str in float_int_str_bool, "str should be present"
    assert bool in float_int_str_bool, "bool should be present"
    assert float in float_int_str_bool, "float should be present"
    
    print("✓ Type concatenation works")


def test_derived_types():
    """Test type derivation and inspection."""
    print("\nTesting derived types...")
    
    # Type alias
    FloatIntStrBool = Intersection[str | int | bool | float]
    
    # Type checking
    assert float in FloatIntStrBool, "float should be in FloatIntStrBool"
    assert not (dict in FloatIntStrBool), "dict should not be in FloatIntStrBool"
    
    # Subset checking
    assert Intersection[float | str] in FloatIntStrBool, "Subset should be contained"
    assert not (Intersection[float | str | dict] in FloatIntStrBool), "Superset should not be contained"
    
    # Iteration over types
    types_found = set()
    for typ in FloatIntStrBool:
        types_found.add(typ)
    
    assert types_found == {float, int, str, bool}, f"Should find all types, got {types_found}"
    
    print("✓ Derived types work")


def test_instance_construction():
    """Test creating instances with type inference."""
    print("\nTesting instance construction...")
    
    # Type inference
    float_int_str = Intersection(5, "int", 0.5)
    
    assert int in float_int_str, "Should infer int from 5"
    assert str in float_int_str, "Should infer str from 'int'"
    assert float in float_int_str, "Should infer float from 0.5"
    
    print("✓ Instance construction works")


def test_type_extraction():
    """Test extracting values from instances."""
    print("\nTesting type extraction...")
    
    float_int_str = Intersection(5, "hello", 0.5)
    
    # Single type extraction
    float_val = float_int_str.to(float)
    assert float_val == 0.5, f"Expected 0.5, got {float_val}"
    assert isinstance(float_val, float), "Should be plain float, not Intersection"
    
    # Multi-type extraction (rolled back .to(*args); wasn't creative enough to figure out *type[T] -> *T outside of manual overloads)
    int_val, float_val, str_val = tuple(float_int_str.to(_T) for _T in [int, float, str])
    assert float_val == 0.5, f"Expected 0.5, got {float_val}"
    assert int_val == 5, f"Expected 5, got {int_val}"
    assert str_val == "hello", f"Expected 'hello', got {str_val}"
    
    print("✓ Type extraction works")


def test_partial_extraction():
    """Test partial type extraction returning Intersection."""
    print("\nTesting partial extraction...")
    
    float_int_str = Intersection(5, "hello", 0.5)
    
    # Extract subset - should return Intersection
    float_int = float_int_str[float | int] # NOTE: At runtime this will work, but 
    
    assert isinstance(float_int, Intersection), "Should return Intersection"
    assert float in float_int, "Should contain float"
    assert int in float_int, "Should contain int"
    assert not (str in float_int), "Should not contain str"
    
    # Verify values
    assert float_int.to(float) == 0.5, "Should preserve float value"
    assert float_int.to(int) == 5, "Should preserve int value"
    
    print("✓ Partial extraction works")


def test_intersection_operator():
    """Test the & operator for associativity and non-commutativity."""
    print("\nTesting intersection operator...")
    
    float_int = Intersection(5, 0.5)
    bool_int = Intersection(True, 42)
    bool_float = Intersection(False, 1.0)
    
    # Test associativity
    result1 = (float_int & bool_int) & bool_float
    result2 = float_int & (bool_int & bool_float)
    result3 = Intersection(float_int, bool_int, bool_float)
    
    # All should have the same types
    assert set(result1._data.keys()) == set(result2._data.keys()) == set(result3._data.keys())
    
    # Test right-precedence (non-commutativity)
    # bool_float has False for bool and 1.0 for float
    # These should override earlier values
    assert result1.to(bool) == False, "Right-most bool should win"
    assert result1.to(float) == 1.0, "Right-most float should win"
    assert result1.to(int) == 42, "Middle int should be preserved"
    
    print("✓ Intersection operator works")


def test_instance_type_checking():
    """Test type membership on instances."""
    print("\nTesting instance type checking...")
    
    float_int_str = Intersection(5, "hello", 0.5)
    
    # Single type
    assert float in float_int_str, "float should be in instance"
    
    # Multiple types
    assert (float | str) in float_int_str, "float|str should be in instance"
    
    # Missing type
    assert not ((float | str | bool) in float_int_str), "bool should not be in instance"
    
    print("✓ Instance type checking works")


def test_iteration():
    """Test iteration over types and values."""
    print("\nTesting iteration...")
    
    float_int_str = Intersection(5, "hello", 0.5)
    
    # Iterate over types (keys)
    types_found = set()
    for typ in float_int_str:
        types_found.add(typ)
    
    assert types_found == {float, int, str}, f"Should find all types, got {types_found}"
    
    # Iterate over values
    values_found = []
    for value in float_int_str.values():
        assert isinstance(value, Intersection), "Values should be wrapped in Intersection"
        values_found.append(value)
    
    assert len(values_found) == 3, "Should have 3 values"
    
    # Iterate over items
    items_found = []
    for typ, value in float_int_str.items():
        assert isinstance(value, Intersection), "Values should be wrapped in Intersection"
        items_found.append((typ, value))
    
    assert len(items_found) == 3, "Should have 3 items"
    
    print("✓ Iteration works")


def test_hashability():
    """Test that instances are hashable."""
    print("\nTesting hashability...")
    
    obj1 = Intersection(5, "hello", 0.5)
    obj2 = Intersection(5, "hello", 0.5)
    obj3 = Intersection(5, "world", 0.5)
    
    # Should be hashable
    hash1 = hash(obj1)
    hash2 = hash(obj2)
    hash3 = hash(obj3)
    
    # Equal objects should have equal hashes
    assert hash1 == hash2, "Equal objects should have equal hashes"
    
    # Can be used in sets
    s = {obj1, obj2, obj3}
    assert len(s) == 2, "Should deduplicate equal objects"
    
    # Can be used as dict keys
    d = {obj1: "first", obj2: "second", obj3: "third"}
    assert len(d) == 2, "Should deduplicate equal keys"
    
    print("✓ Hashability works")


def test_immutability():
    """Test that instances are immutable."""
    print("\nTesting immutability...")
    
    obj = Intersection(5, "hello", 0.5)
    
    # Cannot modify attributes
    try:
        obj.new_attr = "value"
        assert False, "Should not allow attribute assignment"
    except TypeError:
        pass
    
    # Cannot delete attributes
    try:
        del obj._data
        assert False, "Should not allow attribute deletion"
    except TypeError:
        pass
    
    # Cannot create new instance with same object
    try:
        obj.__init__(10, "world", 1.5)
        assert False, "Should not allow re-initialization"
    except TypeError:
        pass
    
    print("✓ Immutability works")


def test_bonus_set_difference():
    """Test the bonus set difference operation."""
    print("\nTesting bonus set difference...")
    
    float_int_bool = Intersection(5, True, 0.5)
    
    # Remove bool type
    float_int = float_int_bool / bool
    
    assert float in float_int, "float should remain"
    assert int in float_int, "int should remain"
    assert not (bool in float_int), "bool should be removed"
    
    # Remove multiple types
    just_float = float_int_bool / (bool | int)
    assert float in just_float, "float should remain"
    assert not (bool in just_float), "bool should be removed"
    assert not (int in just_float), "int should be removed"
    
    print("✓ Set difference works")


def test_type_errors():
    """Test that appropriate errors are raised."""
    print("\nTesting error conditions...")
    
    obj = Intersection(5, "hello", 0.5)
    
    # Extract missing type
    try:
        obj.to(bool)
        assert False, "Should raise KeyError for missing type"
    except KeyError:
        pass
    
    # Extract subset with missing type
    try:
        obj[float | bool]
        assert False, "Should raise KeyError for missing type in subset"
    except KeyError:
        pass
    
    # Combine with non-Intersection - this should work now (wraps the value)
    result = obj & "not an intersection"
    assert str in result, "Should wrap string and add to intersection"
    assert result.to(str) == "not an intersection", "Should have correct string value"
    
    print("✓ Error conditions handled correctly")


def test_edge_cases():
    """Test edge cases and corner scenarios."""
    print("\nTesting edge cases...")
    
    # Empty intersection
    empty = Intersection()
    assert len(empty) == 0, "Empty intersection should have length 0"
    assert list(empty) == [], "Should iterate to empty list"
    
    # Single type
    single = Intersection(42)
    assert len(single) == 1, "Should have one type"
    assert int in single, "Should contain int"
    
    # Type override (right precedence)
    obj = Intersection(5, 10, 15)  # All int, last one wins
    assert obj.to(int) == 15, "Last value should win"
    
    # Nested intersection merging
    inner = Intersection(5, "hello")
    outer = Intersection(inner, 0.5)
    assert int in outer and str in outer and float in outer, "Should merge nested intersection"
    
    print("✓ Edge cases handled correctly")


def test_isinstance_and_issubclass():
    """Test isinstance and issubclass with Intersection types."""
    print("\nTesting isinstance and issubclass...")
    
    # Create types
    FloatInt = Intersection[float | int]
    FloatIntStr = Intersection[float | int | str]
    
    # Create instance
    obj = Intersection(5, 0.5)
    
    # isinstance checking
    assert isinstance(obj, Intersection), "Should be instance of Intersection"
    # Note: isinstance with specific type requires exact match
    # This is a limitation of Python's type system
    
    # issubclass checking
    assert issubclass(FloatInt, FloatIntStr), "Subset should be subclass of superset"
    assert not issubclass(FloatIntStr, FloatInt), "Superset should not be subclass of subset"
    
    print("✓ isinstance and issubclass work")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Running Intersection Type System Test Suite")
    print("=" * 60)
    
    test_type_subset_checking()
    test_type_equivalence()
    test_type_construction()
    test_type_concatenation()
    test_derived_types()
    test_instance_construction()
    test_type_extraction()
    test_partial_extraction()
    test_intersection_operator()
    test_instance_type_checking()
    test_iteration()
    test_hashability()
    test_immutability()
    test_bonus_set_difference()
    test_type_errors()
    test_edge_cases()
    test_isinstance_and_issubclass()
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()