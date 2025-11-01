"""
Interactive demo of Intersection/Intersection types.

Run this file to see all features in action!
"""
from intersection_types import Intersection, IntersectionMeta, make_intersection_type
from typing_extensions import TypeForm as TypeExpr


def demo_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_basic():
    """Demonstrate basic Intersection operations."""
    demo_header("BASIC OPERATIONS")
    
    print("\n# Create a Intersection with three values")
    print(">>> isf = Intersection(5, 'hello', 0.2)")
    isf = Intersection(5, "hello", 0.2)
    print(f"    {isf}")
    print(f"    Type: {type(isf)}")
    
    print("\n# Access values by type")
    print(">>> isf[int]")
    print(f"    {isf[int]}")
    print(">>> isf[str]")
    print(f"    {isf[str]}")
    print(">>> isf[float]")
    print(f"    {isf[float]}")
    
    print("\n# Modify a value")
    print(">>> isf[str] = 'world'")
    isf[str] = "world"
    print(f"    {isf}")


def demo_permutation_invariance():
    """Demonstrate that order doesn't matter."""
    demo_header("PERMUTATION INVARIANCE")
    
    print("\n# Order of arguments doesn't matter")
    print(">>> p1 = Intersection(1, 'hello', 3.14)")
    print(">>> p2 = Intersection('hello', 3.14, 1)")
    p1 = Intersection(1, "hello", 3.14)
    p2 = Intersection("hello", 3.14, 1)
    
    print(f"\n    p1: {p1}")
    print(f"    p2: {p2}")
    print(f"\n>>> p1 == p2")
    print(f"    {p1 == p2}")


def demo_type_constructors():
    """Demonstrate creating Intersection types."""
    demo_header("TYPE CONSTRUCTORS")
    
    print("\n# Define a Intersection type explicitly")
    print(">>> IntStrFloat = Intersection[int | str | float]")
    IntStrFloat = Intersection[int | str | float]
    print(f"    {IntStrFloat}")
    
    print("\n# Create instances of the type")
    print(">>> isf = IntStrFloat(42, 'answer', 2.71)")
    isf = IntStrFloat(42, "answer", 2.71)
    print(f"    {isf}")
    
    print("\n# Define named classes")
    print(">>> class MyIntersection(Intersection[int | str | bool]):")
    print("...     pass")
    class MyIntersection(Intersection[int | str | bool]):
        pass
    
    print(">>> mp = MyIntersection(100, 'test', True)")
    mp = MyIntersection(100, "test", True)
    print(f"    {mp}")


def demo_type_division():
    """Demonstrate type division/extraction."""
    demo_header("TYPE DIVISION")
    
    print("\n# Start with a Intersection type")
    print(">>> FullType = Intersection[int | str | float | bool]")
    FullType = Intersection[int | str | float | bool]
    print(f"    {FullType}")
    
    print("\n# Extract subsets using type division")
    print(">>> IntOnly = FullType[int]")
    IntOnly = FullType[int]
    print(f"    {IntOnly}")
    
    print(">>> NumericTypes = FullType[int | float]")
    NumericTypes = FullType[int | float]
    print(f"    {NumericTypes}")
    
    print("\n# Check containment")
    print(">>> int in IntOnly")
    print(f"    {int in IntOnly}")
    print(">>> str in IntOnly")
    print(f"    {str in IntOnly}")
    print(">>> int in NumericTypes")
    print(f"    {int in NumericTypes}")


def demo_runtime_access():
    """Demonstrate runtime type access."""
    demo_header("RUNTIME TYPE ACCESS")
    
    print("\n# Create a Intersection")
    print(">>> data = Intersection(42, 'hello', 3.14, True)")
    data = Intersection(42, "hello", 3.14, True)
    print(f"    {data}")
    
    print("\n# Extract a subset at runtime")
    print(">>> nums = data[int | float]")
    nums = data[int | float]
    print(f"    {nums}")
    print(f"    Type: {type(nums)}")
    
    print("\n# Access values from the subset")
    print(">>> nums[int]")
    print(f"    {nums[int]}")
    print(">>> nums[float]")
    print(f"    {nums[float]}")


def demo_type_composition():
    """Demonstrate composing types with &."""
    demo_header("TYPE COMPOSITION")
    
    print("\n# Build types incrementally")
    print(">>> Base = Intersection[int | str]")
    Base = Intersection[int | str]
    print(f"    {Base}")
    
    print(">>> Extended = Base & Intersection[float]")
    Extended = Base & Intersection[float]
    print(f"    {Extended}")
    
    print(">>> Full = Extended & Intersection[bool]")
    Full = Extended & Intersection[bool]
    print(f"    {Full}")
    
    print("\n# Alternative: chain operators")
    print(">>> Chained = Intersection[int] & Intersection[str] & Intersection[float] & Intersection[bool]")
    Chained = Intersection[int] & Intersection[str] & Intersection[float] & Intersection[bool]
    print(f"    {Chained}")
    
    print(f"\n>>> Full == Chained")
    print(f"    {Full == Chained}")


def demo_instance_composition():
    """Demonstrate combining Intersection instances."""
    demo_header("INSTANCE COMPOSITION")
    
    print("\n# Create separate Intersections")
    print(">>> p1 = Intersection(42, 'hello')")
    p1 = Intersection(42, "hello")
    print(f"    {p1}")
    
    print(">>> p2 = Intersection(3.14, True)")
    p2 = Intersection(3.14, True)
    print(f"    {p2}")
    
    print("\n# Combine them with &")
    print(">>> combined = p1 & p2")
    combined = p1 & p2
    print(f"    {combined}")
    print(f"    Type: {type(combined)}")


def demo_with_changes():
    """Demonstrate updating Intersections with with_changes."""
    demo_header("UPDATING WITH with_changes()")
    
    print("\n# Start with a Intersection")
    print(">>> original = Intersection(1, 'hello', 3.14)")
    original = Intersection(1, "hello", 3.14)
    print(f"    {original}")
    
    print("\n# Create update Intersections")
    print(">>> update1 = Intersection(2, 'world')")
    update1 = Intersection(2, "world")
    print(f"    {update1}")
    
    print(">>> update2 = Intersection(True)")
    update2 = Intersection(True)
    print(f"    {update2}")
    
    print("\n# Apply updates left-to-right")
    print(">>> modified = original.with_changes(update1, update2)")
    modified = original.with_changes(update1, update2)
    print(f"    {modified}")
    
    print("\n# Later values override earlier ones")
    print(">>> final = modified.with_changes(Intersection(False), Intersection(99))")
    final = modified.with_changes(Intersection(False), Intersection(99))
    print(f"    {final}")


def demo_type_flattening():
    """Demonstrate automatic flattening of nested Intersections."""
    demo_header("TYPE FLATTENING")
    
    print("\n# Nested Intersections are automatically flattened")
    print(">>> T1 = Intersection[int | str | float]")
    T1 = Intersection[int | str | float]
    print(f"    {T1}")
    
    print("\n>>> T2 = Intersection[Intersection[int | str] | float]")
    T2 = Intersection[Intersection[int | str] | float]
    print(f"    {T2}")
    
    print("\n>>> T3 = Intersection[int | Intersection[Intersection[float] | str]]")
    T3 = Intersection[int | Intersection[Intersection[float] | str]]
    print(f"    {T3}")
    
    print("\n# All three are equivalent!")
    print(f">>> T1 == T2")
    print(f"    {T1 == T2}")
    print(f">>> T2 == T3")
    print(f"    {T2 == T3}")
    print(f">>> T1 == T3")
    print(f"    {T1 == T3}")


def demo_containment():
    """Demonstrate type containment checks."""
    demo_header("TYPE CONTAINMENT")
    
    print("\n# Create Intersection types")
    print(">>> Small = Intersection[int | str]")
    Small = Intersection[int | str]
    print(f"    {Small}")
    
    print(">>> Large = Intersection[int | str | float | bool]")
    Large = Intersection[int | str | float | bool]
    print(f"    {Large}")
    
    print("\n# Check single type containment")
    print(">>> int in Small")
    print(f"    {int in Small}")
    print(">>> float in Small")
    print(f"    {float in Small}")
    
    print("\n# Check Intersection type containment (subset relation)")
    print(">>> Small in Large")
    print(f"    {Small in Large}")
    print(">>> Large in Small")
    print(f"    {Large in Small}")


def demo_real_world_example():
    """Demonstrate a real-world use case."""
    demo_header("REAL-WORLD EXAMPLE: User Profile")
    
    print("\n# Define domain types")
    print(">>> UserProfile = Intersection[int | str | bool]  # id, name, is_active")
    print(">>> ContactInfo = Intersection[str | int]          # email, phone")
    print(">>> Preferences = Intersection[bool | str]         # notifications, theme")
    
    UserProfile = Intersection[int | str | bool]
    ContactInfo = Intersection[str | int]
    Preferences = Intersection[bool | str]
    
    print("\n# Create individual pieces")
    print(">>> profile = UserProfile(12345, 'Alice', True)")
    profile = UserProfile(12345, "Alice", True)
    print(f"    User ID: {profile[int]}, Name: {profile[str]}, Active: {profile[bool]}")
    
    print("\n>>> contact = ContactInfo('alice@example.com', 5551234)")
    contact = ContactInfo("alice@example.com", 5551234)
    print(f"    Email: {contact[str]}, Phone: {contact[int]}")
    
    print("\n>>> prefs = Preferences(True, 'dark')")
    prefs = Preferences(True, "dark")
    print(f"    Notifications: {prefs[bool]}, Theme: {prefs[str]}")
    
    print("\n# Combine into complete user data")
    print(">>> user = profile.with_changes(")
    print("...     Intersection('alice@example.com'),")
    print("...     Intersection(5551234),")
    print("...     prefs")
    print("... )")
    user = profile.with_changes(
        Intersection("alice@example.com"),
        Intersection(5551234),
        prefs
    )
    print(f"    {user}")
    
    print("\n# Access specific fields by type")
    print(">>> user[int]    # User ID")
    print(f"    {user[int]}")
    print(">>> user[str]    # Theme (last string value)")
    print(f"    {user[str]}")
    print(">>> user[bool]   # Notifications")
    print(f"    {user[bool]}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  PRODUCT TYPE SYSTEM - INTERACTIVE DEMO")
    print("=" * 70)
    print("\n  Demonstrating all features of Intersection/Intersection types")
    print("  for Python 3.14+")
    print()
    
    demos = [
        demo_basic,
        demo_permutation_invariance,
        demo_type_constructors,
        demo_type_division,
        demo_runtime_access,
        demo_type_composition,
        demo_instance_composition,
        demo_with_changes,
        demo_type_flattening,
        demo_containment,
        demo_real_world_example,
    ]
    
    for demo in demos:
        demo()
    
    print("\n" + "=" * 70)
    print("  END OF DEMO")
    print("=" * 70)
    print("\n  For more information, see README.md")
    print()


if __name__ == "__main__":
    main()
