"""Tests for the ndjson extension."""

import pytest
import tempfile
from pathlib import Path

from conjunction_types import Conjunction
from conjunction_types.ndjson import NDJSONFile, ConjunctionSerializer, TypeRegistry


def _make_conjunction_with_types(type_value_dict):
    """Helper to create Conjunction with explicit type keys."""
    result = Conjunction.__new__(Conjunction)
    object.__setattr__(result, '_data', type_value_dict)
    object.__setattr__(result, '_hash', None)
    return result


class TestBasicSerialization:
    """Test basic serialization of simple types."""

    def test_serialize_simple_types(self):
        """Serialize and deserialize basic Python types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            c1 = Conjunction(42, 'hello', 3.14)
            c2 = Conjunction(100, 'world', 2.71)

            file.append(c1)
            file.append(c2)

            results = list(file.read())

            assert len(results) == 2
            assert results[0].to(int) == 42
            assert results[0].to(str) == 'hello'
            assert results[0].to(float) == 3.14

            assert results[1].to(int) == 100
            assert results[1].to(str) == 'world'
            assert results[1].to(float) == 2.71
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_serialize_collections(self):
        """Serialize collections (list, dict, set, tuple)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            c = Conjunction(
                [1, 2, 3],
                {'key': 'value'},
                (1, 2, 3),
                123
            )

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            assert results[0].to(list) == [1, 2, 3]
            assert results[0].to(dict) == {'key': 'value'}
            assert results[0].to(tuple) == (1, 2, 3)
            assert results[0].to(int) == 123
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_write_all(self):
        """Test write_all method."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            conjunctions = [
                Conjunction(1, 'a'),
                Conjunction(2, 'b'),
                Conjunction(3, 'c'),
            ]

            file.write_all(conjunctions)
            results = list(file.read())

            assert len(results) == 3
            assert results[0].to(int) == 1
            assert results[1].to(int) == 2
            assert results[2].to(int) == 3
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestGenericTypes:
    """Test serialization of generic types like list[int], dict[str, int]."""

    def test_generic_list_types(self):
        """Distinguish between list[int] and list[str]."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            c = _make_conjunction_with_types({
                list[int]: [1, 2, 3],
                list[str]: ['a', 'b', 'c']
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            assert results[0].to(list[int]) == [1, 2, 3]
            assert results[0].to(list[str]) == ['a', 'b', 'c']

            # Verify types are distinct
            assert list[int] in results[0]
            assert list[str] in results[0]
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_generic_dict_types(self):
        """Distinguish between dict[str, int] and dict[str, str]."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            c = _make_conjunction_with_types({
                dict[str, int]: {'x': 10, 'y': 20},
                dict[str, str]: {'name': 'Alice', 'city': 'NYC'}
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            assert results[0].to(dict[str, int]) == {'x': 10, 'y': 20}
            assert results[0].to(dict[str, str]) == {'name': 'Alice', 'city': 'NYC'}
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_mixed_generic_and_simple_types(self):
        """Mix generic and simple types in one Conjunction."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            c = _make_conjunction_with_types({
                int: 42,
                str: 'hello',
                list[int]: [1, 2, 3],
                dict[str, str]: {'key': 'value'}
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            assert results[0].to(int) == 42
            assert results[0].to(str) == 'hello'
            assert results[0].to(list[int]) == [1, 2, 3]
            assert results[0].to(dict[str, str]) == {'key': 'value'}
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestTypeRegistry:
    """Test custom type serialization with TypeRegistry."""

    def test_custom_type_path(self):
        """Register custom serializer for Path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            registry = TypeRegistry()
            registry.register(
                Path,
                serializer=str,
                deserializer=Path,
            )

            file = NDJSONFile(tmp_path, registry=registry)

            c = _make_conjunction_with_types({
                Path: Path('/tmp'),
                str: 'config',
                int: 123
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            assert results[0].to(Path) == Path('/tmp')
            assert results[0].to(str) == 'config'
            assert results[0].to(int) == 123
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_custom_type_serialization(self):
        """Test custom class serialization using mint()."""
        from conjunction_types.ndjson import mint

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __eq__(self, other):
                return self.x == other.x and self.y == other.y

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            # Use mint() to register the custom type
            PointType = mint(
                'Point',
                Point,
                serializer=lambda p: {'x': p.x, 'y': p.y},
                deserializer=lambda d: Point(d['x'], d['y'])
            )

            file = NDJSONFile(tmp_path)

            c = _make_conjunction_with_types({
                PointType: Point(10, 20),
                str: 'origin'
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            point = results[0].to(PointType)
            assert point.x == 10
            assert point.y == 20
            assert results[0].to(str) == 'origin'
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_register_type_for_deserialization(self):
        """Test register_type for making types available in eval namespace."""

        class CustomType:
            def __init__(self, value):
                self.value = value

        registry = TypeRegistry()
        registry.register_type('CustomType', CustomType)

        assert 'CustomType' in registry._safe_globals
        assert registry._safe_globals['CustomType'] is CustomType


class TestConjunctionSerializer:
    """Test ConjunctionSerializer directly."""

    def test_to_json_format(self):
        """Verify the JSON format structure."""
        serializer = ConjunctionSerializer()

        c = Conjunction(42, 'hello')
        data = serializer.to_json(c)

        assert '__conjunction_types__' in data
        assert len(data['__conjunction_types__']) == 2

        # Check metadata structure
        for entry in data['__conjunction_types__']:
            assert 'type' in entry
            assert 'key' in entry

    def test_from_json_roundtrip(self):
        """Test roundtrip serialization."""
        serializer = ConjunctionSerializer()

        original = Conjunction(42, 'hello', 3.14, True)
        data = serializer.to_json(original)
        restored = serializer.from_json(data)

        assert restored.to(int) == 42
        assert restored.to(str) == 'hello'
        assert restored.to(float) == 3.14
        assert restored.to(bool) is True

    def test_generic_types_in_json(self):
        """Verify generic types are preserved in JSON."""
        serializer = ConjunctionSerializer()

        c = _make_conjunction_with_types({
            list[int]: [1, 2, 3],
            list[str]: ['a', 'b']
        })

        data = serializer.to_json(c)

        # Check that type representations are correct
        types = [entry['type'] for entry in data['__conjunction_types__']]
        assert 'list[int]' in types
        assert 'list[str]' in types


class TestNDJSONFile:
    """Test NDJSONFile utilities."""

    def test_count_lines(self):
        """Test count_lines method."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            assert file.count_lines() == 0

            file.append(Conjunction(1))
            file.append(Conjunction(2))
            file.append(Conjunction(3))

            assert file.count_lines() == 3
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_read_raw(self):
        """Test reading raw JSON dicts."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            file = NDJSONFile(tmp_path)

            c = Conjunction(42, 'hello')
            file.append(c)

            raw_data = list(file.read_raw())

            assert len(raw_data) == 1
            assert '__conjunction_types__' in raw_data[0]
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_nonexistent_file_read(self):
        """Reading from nonexistent file should return empty iterator."""
        file = NDJSONFile('/nonexistent/path/file.ndjson')
        results = list(file.read())
        assert len(results) == 0

    def test_empty_lines_skipped(self):
        """Empty lines in NDJSON file should be skipped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            # Write file with empty lines
            import json
            with open(tmp_path, 'w') as f:
                serializer = ConjunctionSerializer()
                data1 = serializer.to_json(Conjunction(1))
                data2 = serializer.to_json(Conjunction(2))
                f.write(json.dumps(data1) + '\n')
                f.write('\n')  # Empty line
                f.write(json.dumps(data2) + '\n')
                f.write('\n')  # Another empty line

            file = NDJSONFile(tmp_path)
            results = list(file.read())

            assert len(results) == 2
            assert results[0].to(int) == 1
            assert results[1].to(int) == 2
        finally:
            Path(tmp_path).unlink(missing_ok=True)


class TestMint:
    """Test the mint() function for type registration."""

    def test_mint_generic_types(self):
        """Test minting generic types like list[int]."""
        from conjunction_types.ndjson import mint

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            # Mint generic types
            MyIntList = mint('MyIntList', list[int])
            MyStrList = mint('MyStrList', list[str])

            file = NDJSONFile(tmp_path)

            c = _make_conjunction_with_types({
                MyIntList: [1, 2, 3],
                MyStrList: ['a', 'b']
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            assert results[0].to(MyIntList) == [1, 2, 3]
            assert results[0].to(MyStrList) == ['a', 'b']

            # Check that the JSON uses stable names
            raw = list(file.read_raw())
            type_names = [t['type'] for t in raw[0]['__conjunction_types__']]
            assert 'MyIntList' in type_names
            assert 'MyStrList' in type_names
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_mint_custom_type_with_serializers(self):
        """Test minting a custom type with custom serializers."""
        from conjunction_types.ndjson import mint

        class Vector:
            def __init__(self, x, y, z):
                self.x, self.y, self.z = x, y, z

            def __eq__(self, other):
                return (self.x, self.y, self.z) == (other.x, other.y, other.z)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.ndjson', delete=False) as f:
            tmp_path = f.name

        try:
            VectorType = mint(
                'Vector3D',
                Vector,
                serializer=lambda v: [v.x, v.y, v.z],
                deserializer=lambda lst: Vector(*lst)
            )

            file = NDJSONFile(tmp_path)

            c = _make_conjunction_with_types({
                VectorType: Vector(1, 2, 3),
                str: 'direction'
            })

            file.append(c)
            results = list(file.read())

            assert len(results) == 1
            vec = results[0].to(VectorType)
            assert vec == Vector(1, 2, 3)
            assert results[0].to(str) == 'direction'
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_mint_returns_callable_constructor(self):
        """Test that mint() returns a callable constructor, not the type itself."""
        from conjunction_types.ndjson import mint

        original = list[int]
        MyList = mint('MyList', original)

        # Should return a callable constructor, not the type itself
        assert callable(MyList)
        assert MyList is not original

        # Constructor should create instances
        instance = MyList([1, 2, 3])
        assert instance == [1, 2, 3]
        assert isinstance(instance, list)

    def test_mint_duplicate_registration_same_name(self):
        """Test that re-registering with the same name is idempotent."""
        from conjunction_types.ndjson import mint

        typ = list[int]
        MyList1 = mint('MyList_Test1', typ)
        MyList2 = mint('MyList_Test1', typ)  # Same name, same type

        assert MyList1 is MyList2

    def test_mint_same_type_different_names_allowed(self):
        """Test that registering the same type with different names is allowed.

        This creates distinct constructors with unique identities, allowing
        multiple 'slots' for the same base type in a Conjunction.
        """
        from conjunction_types.ndjson import mint

        typ = list[str]
        Name1 = mint('Name1_Test2', typ)
        Name2 = mint('Name2_Test2', typ)

        # Different names should create different constructors
        assert Name1 is not Name2
        assert callable(Name1)
        assert callable(Name2)

    def test_mint_duplicate_name_different_type_raises(self):
        """Test that using the same name for different types raises."""
        from conjunction_types.ndjson import mint

        mint('SharedName', list[int])

        with pytest.raises(ValueError, match="already registered"):
            mint('SharedName', list[str])


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_missing_conjunction_types_key(self):
        """from_json should raise ValueError for missing __conjunction_types__."""
        serializer = ConjunctionSerializer()

        with pytest.raises(ValueError, match="Missing '__conjunction_types__'"):
            serializer.from_json({'foo': 'bar'})

    def test_empty_conjunction_types(self):
        """Empty Conjunction types should raise ValueError."""
        serializer = ConjunctionSerializer()

        with pytest.raises(ValueError, match="Cannot create empty Conjunction"):
            serializer.from_json({'__conjunction_types__': []})

    def test_missing_value_key(self):
        """Missing value key should raise ValueError."""
        serializer = ConjunctionSerializer()

        data = {
            '__conjunction_types__': [
                {'type': 'int', 'key': 'int_0'}
            ]
            # Missing 'int_0' key
        }

        with pytest.raises(ValueError, match="Missing value for key"):
            serializer.from_json(data)

    def test_non_json_serializable_type(self):
        """Non-JSON-serializable types should raise TypeError."""

        class NotSerializable:
            pass

        serializer = ConjunctionSerializer()
        c = Conjunction(NotSerializable())

        with pytest.raises(TypeError, match="not JSON-serializable"):
            serializer.to_json(c)

    def test_unknown_type_deserialization(self):
        """Unknown types in deserialization should raise ValueError."""
        serializer = ConjunctionSerializer()

        data = {
            '__conjunction_types__': [
                {'type': 'UnknownCustomType', 'key': 'type_0'}
            ],
            'type_0': 'some_value'
        }

        with pytest.raises(ValueError, match="Cannot deserialize type"):
            serializer.from_json(data)
