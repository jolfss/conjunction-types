import pytest
from conjunction_types import Conjunction


class TestTypeSubsetChecking:
    """Test isinstance-style subset checking on types."""

    def test_subset_in_superset(self):
        """Conjunction[float|str] should be in Conjunction[float|int|str]"""
        float_int_str = Conjunction[float | int | str]
        float_str = Conjunction[float | str]
        assert float_str in float_int_str

    def test_superset_not_in_subset(self):
        """Superset should not be in subset"""
        float_int_str = Conjunction[float | int | str]
        assert not (Conjunction[float | int | str | bool] in float_int_str)

    def test_single_type_checking(self):
        """Single types should be checkable"""
        float_int_str = Conjunction[float | int | str]
        assert float in float_int_str
        assert int in float_int_str
        assert dict not in float_int_str

    def test_generic_type_checking(self):
        """Generic types like dict[str,str] should be distinguished"""
        float_int_str = Conjunction[float | int | str]
        float_int_str_dictstrstr = float_int_str & dict[str, str]

        assert dict[str, str] in float_int_str_dictstrstr
        assert dict[str, int] not in float_int_str_dictstrstr

    def test_union_type_checking(self):
        """Unions are treated as conjunctions inside conjunctions"""
        float_int_str = Conjunction[float | int | str]
        assert int | str in float_int_str

    def test_conjunction_class_union_behavior(self):
        """Conjunction classes act as their syntactic union counterpart"""
        float_int_str = Conjunction[float | int | str]
        float_int_str_dictstrstr = float_int_str & dict[str, str]

        assert float_int_str | list not in float_int_str_dictstrstr
        assert float_int_str & list not in float_int_str_dictstrstr
        assert dict[str, str] & float_int_str in float_int_str_dictstrstr


class TestTypeEquivalence:
    """Test type equality and permutation invariance."""

    def test_permutation_invariance(self):
        """Types should be equal regardless of order"""
        assert Conjunction[float | str] == Conjunction[str | float]

    def test_conjunction_operator(self):
        """& should combine types"""
        assert (Conjunction[float] & Conjunction[str]) == Conjunction[str | float]

    def test_conjunction_flattening(self):
        """Should flatten nested Conjunctions"""
        assert Conjunction[Conjunction[float] & str] == Conjunction[float | str]

    def test_union_distribution(self):
        """Should distribute over union"""
        assert Conjunction[float | Conjunction[str]] == Conjunction[float | str]

    def test_generic_type_distinction(self):
        """Different parametrizations should not be equal"""
        assert Conjunction[dict[str, str]] != Conjunction[dict[str, int]]
        assert Conjunction[dict[str, dict[str, int]]] == Conjunction[dict[str, dict[str, int]]]

    def test_nested_flatten_equivalence(self):
        """Complex nested structures should flatten correctly"""
        assert Conjunction[Conjunction[int | Conjunction[dict[str, int]]] & bool] == \
               Conjunction[int | dict[str, int] | bool]


class TestTypeConstruction:
    """Test type construction with getitem."""

    def test_basic_construction(self):
        """Basic type construction should work"""
        str_type = Conjunction[str]
        assert str in str_type

    def test_multi_type_construction(self):
        """Multi-type construction should work"""
        str_int = Conjunction[str | int]
        assert str in str_int and int in str_int

    def test_invalid_subset_extraction(self):
        """Trying to extract bool from str|int should fail"""
        str_int_instance = Conjunction[str | int]("hello", 5)
        with pytest.raises(KeyError):
            str_int_instance[bool]


class TestTypeConcatenation:
    """Test associative type concatenation."""

    def test_complex_concatenation(self):
        """Create instance through concatenation"""
        q = Conjunction("cactus", Conjunction("string"), Conjunction(True))
        assert str in q and bool in q

    def test_simple_concatenation(self):
        """Simple concatenation"""
        x = Conjunction(5) & "Any"
        assert int in x and str in x

    def test_nested_concatenation(self):
        """Nested concatenation should work"""
        y = Conjunction(Conjunction(Conjunction(5) & Conjunction(15) & 2.0))
        assert int in y and float in y

    def test_multi_level_concatenation(self):
        """Multi-level concatenation"""
        float_int_str_bool = Conjunction(Conjunction(5) & "a string") & Conjunction(True, 0.3)

        assert int in float_int_str_bool
        assert str in float_int_str_bool
        assert bool in float_int_str_bool
        assert float in float_int_str_bool


class TestDerivedTypes:
    """Test type derivation and inspection."""

    def test_type_alias(self):
        """Type alias should work"""
        FloatIntStrBool = Conjunction[str | int | bool | float]

        assert float in FloatIntStrBool
        assert not (dict in FloatIntStrBool)

    def test_subset_checking_on_alias(self):
        """Subset checking on type alias"""
        FloatIntStrBool = Conjunction[str | int | bool | float]

        assert Conjunction[float | str] in FloatIntStrBool
        assert not (Conjunction[float | str | dict] in FloatIntStrBool)

    def test_iteration_over_types(self):
        """Should be able to iterate over component types"""
        FloatIntStrBool = Conjunction[str | int | bool | float]

        types_found = set()
        for typ in FloatIntStrBool:
            types_found.add(typ)

        assert types_found == {float, int, str, bool}


class TestInstanceConstruction:
    """Test creating instances with type inference."""

    def test_type_inference(self):
        """Should infer types from values"""
        float_int_str = Conjunction(5, "int", 0.5)

        assert int in float_int_str
        assert str in float_int_str
        assert float in float_int_str


class TestTypeExtraction:
    """Test extracting values from instances."""

    def test_single_type_extraction(self):
        """Should extract single values by type"""
        float_int_str = Conjunction(5, "hello", 0.5)

        float_val = float_int_str.to(float)
        assert float_val == 0.5
        assert isinstance(float_val, float)

    def test_multi_type_extraction(self):
        """Should extract multiple values"""
        float_int_str = Conjunction(5, "hello", 0.5)

        int_val, float_val, str_val = tuple(float_int_str.to(_T) for _T in [int, float, str])
        assert float_val == 0.5
        assert int_val == 5
        assert str_val == "hello"


class TestPartialExtraction:
    """Test partial type extraction returning Conjunction."""

    def test_subset_extraction(self):
        """Extract subset should return Conjunction"""
        float_int_str = Conjunction(5, "hello", 0.5)

        float_int = float_int_str[float | int]

        assert isinstance(float_int, Conjunction)
        assert float in float_int
        assert int in float_int
        assert not (str in float_int)

    def test_value_preservation(self):
        """Values should be preserved in partial extraction"""
        float_int_str = Conjunction(5, "hello", 0.5)
        float_int = float_int_str[float | int]

        assert float_int.to(float) == 0.5
        assert float_int.to(int) == 5


class TestConjunctionOperator:
    """Test the & operator for associativity and non-commutativity."""

    def test_associativity(self):
        """Conjunction should be associative"""
        float_int = Conjunction(5, 0.5)
        bool_int = Conjunction(True, 42)
        bool_float = Conjunction(False, 1.0)

        result1 = (float_int & bool_int) & bool_float
        result2 = float_int & (bool_int & bool_float)
        result3 = Conjunction(float_int, bool_int, bool_float)

        assert set(result1._data.keys()) == set(result2._data.keys()) == set(result3._data.keys())

    def test_right_precedence(self):
        """Right-most values should win (non-commutativity)"""
        float_int = Conjunction(5, 0.5)
        bool_int = Conjunction(True, 42)
        bool_float = Conjunction(False, 1.0)

        result = (float_int & bool_int) & bool_float

        assert result.to(bool) == False
        assert result.to(float) == 1.0
        assert result.to(int) == 42


class TestInstanceTypeChecking:
    """Test type membership on instances."""

    def test_single_type_membership(self):
        """Single type should be checkable"""
        float_int_str = Conjunction(5, "hello", 0.5)
        assert float in float_int_str

    def test_multiple_type_membership(self):
        """Multiple types should be checkable"""
        float_int_str = Conjunction(5, "hello", 0.5)
        assert (float | str) in float_int_str

    def test_missing_type_membership(self):
        """Missing type should return False"""
        float_int_str = Conjunction(5, "hello", 0.5)
        assert not ((float | str | bool) in float_int_str)


class TestIteration:
    """Test iteration over types and values."""

    def test_iterate_types(self):
        """Should iterate over types (keys)"""
        float_int_str = Conjunction(5, "hello", 0.5)

        types_found = set()
        for typ in float_int_str:
            types_found.add(typ)

        assert types_found == {float, int, str}

    def test_iterate_values(self):
        """Should iterate over values wrapped in Conjunction"""
        float_int_str = Conjunction(5, "hello", 0.5)

        values_found = []
        for value in float_int_str.values():
            assert isinstance(value, Conjunction)
            values_found.append(value)

        assert len(values_found) == 3

    def test_iterate_items(self):
        """Should iterate over (type, value) pairs"""
        float_int_str = Conjunction(5, "hello", 0.5)

        items_found = []
        for typ, value in float_int_str.items():
            assert isinstance(value, Conjunction)
            items_found.append((typ, value))

        assert len(items_found) == 3


class TestHashability:
    """Test that instances are hashable."""

    def test_hash_consistency(self):
        """Equal objects should have equal hashes"""
        obj1 = Conjunction(5, "hello", 0.5)
        obj2 = Conjunction(5, "hello", 0.5)
        obj3 = Conjunction(5, "world", 0.5)

        hash1 = hash(obj1)
        hash2 = hash(obj2)
        hash3 = hash(obj3)

        assert hash1 == hash2

    def test_use_in_sets(self):
        """Should be usable in sets"""
        obj1 = Conjunction(5, "hello", 0.5)
        obj2 = Conjunction(5, "hello", 0.5)
        obj3 = Conjunction(5, "world", 0.5)

        s = {obj1, obj2, obj3}
        assert len(s) == 2

    def test_use_as_dict_keys(self):
        """Should be usable as dict keys"""
        obj1 = Conjunction(5, "hello", 0.5)
        obj2 = Conjunction(5, "hello", 0.5)
        obj3 = Conjunction(5, "world", 0.5)

        d = {obj1: "first", obj2: "second", obj3: "third"}
        assert len(d) == 2


class TestImmutability:
    """Test that instances are immutable."""

    def test_no_attribute_assignment(self):
        """Should not allow attribute assignment"""
        obj = Conjunction(5, "hello", 0.5)

        with pytest.raises(TypeError):
            obj.new_attr = "value"

    def test_no_attribute_deletion(self):
        """Should not allow attribute deletion"""
        obj = Conjunction(5, "hello", 0.5)

        with pytest.raises(TypeError):
            del obj._data

    def test_no_reinitialization(self):
        """Should not allow re-initialization"""
        obj = Conjunction(5, "hello", 0.5)

        with pytest.raises(TypeError):
            obj.__init__(10, "world", 1.5)


class TestSetDifference:
    """Test the bonus set difference operation."""

    def test_remove_single_type(self):
        """Should remove single type"""
        float_int_bool = Conjunction(5, True, 0.5)
        float_int = float_int_bool / bool

        assert float in float_int
        assert int in float_int
        assert not (bool in float_int)

    def test_remove_multiple_types(self):
        """Should remove multiple types"""
        float_int_bool = Conjunction(5, True, 0.5)
        just_float = float_int_bool / (bool | int)

        assert float in just_float
        assert not (bool in just_float)
        assert not (int in just_float)


class TestTypeErrors:
    """Test that appropriate errors are raised."""

    def test_extract_missing_type(self):
        """Should raise KeyError for missing type"""
        obj = Conjunction(5, "hello", 0.5)

        with pytest.raises(KeyError):
            obj.to(bool)

    def test_extract_subset_with_missing_type(self):
        """Should raise KeyError for missing type in subset"""
        obj = Conjunction(5, "hello", 0.5)

        with pytest.raises(KeyError):
            obj[float | bool]

    def test_combine_with_non_conjunction(self):
        """Should wrap non-Conjunction values"""
        obj = Conjunction(5, "hello", 0.5)
        result = obj & "not an conjunction"

        assert str in result
        # The new string should override the old one
        assert result.to(str) == "not an conjunction"


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_empty_conjunction(self):
        """Empty conjunction should work"""
        empty = Conjunction()
        assert len(empty) == 0
        assert list(empty) == []

    def test_single_type(self):
        """Single type conjunction should work"""
        single = Conjunction(42)
        assert len(single) == 1
        assert int in single

    def test_type_override(self):
        """Last value should win (right precedence)"""
        obj = Conjunction(5, 10, 15)
        assert obj.to(int) == 15

    def test_nested_conjunction_merging(self):
        """Nested conjunctions should merge"""
        inner = Conjunction(5, "hello")
        outer = Conjunction(inner, 0.5)

        assert int in outer and str in outer and float in outer


class TestIsInstanceAndIsSubclass:
    """Test isinstance and issubclass with Conjunction types."""

    def test_isinstance_base(self):
        """Should be instance of base Conjunction"""
        obj = Conjunction(5, 0.5)
        assert isinstance(obj, Conjunction)

    def test_issubclass_subset(self):
        """Subset should be subclass of superset"""
        FloatInt = Conjunction[float | int]
        FloatIntStr = Conjunction[float | int | str]

        assert issubclass(FloatInt, FloatIntStr)

    def test_issubclass_not_superset(self):
        """Superset should not be subclass of subset"""
        FloatInt = Conjunction[float | int]
        FloatIntStr = Conjunction[float | int | str]

        assert not issubclass(FloatIntStr, FloatInt)
