"""
Type hint verification - demonstrates that all type hints are properly defined
and will be visible in IDEs like PyCharm, VSCode with Pylance, etc.
"""
from intersection_types import Intersection, IntersectionMeta, make_intersection_type
from typing_extensions import TypeForm as TypeExpr


# Example 2: Type-hinted Intersection instance
my_intersection: Intersection[int | str | float] = Intersection(42, "hello", 3.14)

# Example 3: Type-hinted access - single value
int_value: Intersection[int] = my_intersection[int]
str_value: Intersection[str] = my_intersection[str]

# Example 4: Type-hinted access - multiple values (returns Intersection)
subset: Intersection[int | str] = my_intersection[int | str]

# Example 5: Type-hinted type division
JustInt: IntersectionMeta[int] = IntStrFloat[int]
IntAndStr: IntersectionMeta[int | str] = IntStrFloat[int | str]

# Example 6: Type-hinted composition
Base: IntersectionMeta[int | str] = Intersection[int] & Intersection[str]
Extended: IntersectionMeta[int | str | float] = Base & Intersection[float]

# Example 7: Type-hinted instance composition  
p1: Intersection[int | str] = Intersection(1, "hi")
p2: Intersection[float | bool] = Intersection(3.14, True)
combined: Intersection[int | str | float | bool] = p1 & p2

# Example 8: Type-hinted with_changes
original: Intersection[int | str] = Intersection(1, "hello")
updated: Intersection[int | str | bool] = original.with_changes(Intersection(True))

# Example 9: Type-hinted helper function
MyType: IntersectionMeta = make_intersection_type(int, str, float, bool)
instance: Intersection = MyType(1, "test", 2.5, False)

# Example 10: Type-hinted function signatures
def process_intersection(p: Intersection[int | str | float]) -> int:
    """
    Process a Intersection containing int, str, and float.
    
    The IDE will show proper type hints for the parameter and return value.
    """
    return p[int] * 2

def create_intersection(i: int, s: str, f: float) -> Intersection[int | str | float]:
    """
    Create a Intersection from individual values.
    
    The IDE will show proper type hints.
    """
    return Intersection(i, s, f)

def get_intersection_type() -> IntersectionMeta[int | str]:
    """
    Return a Intersection type constructor.
    
    The IDE will show this returns a IntersectionMeta.
    """
    return Intersection[int | str]

# Example 11: Type-hinted type alias instead of subclassing
MyIntersection = Intersection[int | str | bool]

# Create an instance with proper type hints
my_instance: Intersection[int | str | bool] = MyIntersection(42, "test", True)
result: int = my_instance[int] * 2
message: str = my_instance[str]

print("✓ All type hints are properly defined and IDE-inspectable!")
print(f"  IntStrFloat type: {IntStrFloat}")
print(f"  my_intersection value: {my_intersection}")
print(f"  int_value: {int_value}")
print(f"  Combined intersection: {combined}")
print(f"  MyIntersection instance: {my_instance}")
