# The planned functionality of the Intersection type
# An immutable, progressive type 

from intersection_types import Intersection
from typing import Union, reveal_type

#
# intersection type
#
# subset subclassing (note: ... isn't supported unless we use commas Intersection[A,B,C,...])
isinstance(Intersection[float|int|str|...], float_int_str) # True
isinstance(Intersection[float|str], float_int_str) # False
isinstance(Intersection[T], generic_with_T[T]) # True iff generic_with_T : Intersection[T|...]
isinstance(T, generic_with_T.to(T)) # True iff generic_with_T : Intersection[T|...]

# type equivalence
Intersection[float|str] == Intersection[str|float] # Permutation invariance
(Intersection[float] & Intersection[str]) == Intersection[str|float] # Intersection operator
Intersection[Intersection[float] & str] == Intersection[float|str] # Intersection flattening
Intersection[float | Intersection[str]] == Intersection[float|str] # NOTE: & isn't implemented for all types, so all union operators are treated as & operators inside an Intersection[...]. ("Intersect distributes over sum").

# type construction with getitem 
Intersection[str] == Intersection[str|...][str]
Intersection[str|int] == Intersection[str|int|...][str|int]
Intersection[str|int][bool] # fails since bool not in (str | int)

# type-concatenation (associative, not commutative)
float_int_str_bool : Intersection[float | int | str | bool] = Intersection(Intersection(5) & "a string") & Intersection(True, 0.3)

# derived types
type FloatIntStrBool = Intersection[str | int | bool | str]
FloatIntStrBool is float 
not FloatIntStrBool is dict
float in FloatIntStrBool # True
Intersection[float | str] in FloatIntStrBool # True
Intersection[float | str | dict] in FloatIntStrBool # False

# iteration
for _type in FloatIntStrBool: ...
# _type in {float, int, str, bool}
#
#
#

#
#  intersection instances
#
# type-constructor (infers types and dynamically creates corresponding class)
float_int_str : Intersection[float | int | str] = Intersection(5, "int", 0.5)

# fully-resolved types still return an intersection
float_intersect : Intersection[float] = float_int_str[float] 
_float : float 

# need to be able to hash

# to extract values, use .to(*types) to get a tuple of the types 
_float : float = float_int_str.to(float)
_float, _int, _str = float_int_str.to(float, int, str)

# type inspection (also works on the type itself)
float in float_int_str # True
float | str in float_int_str # True
float | str | bool in float_int_str # False

# iteration
for _type in float_int_str: ... # .keys()
# _type in {float, int, str}
for _type, _value in float_int_str.items(): ...
# _type in {float, int, str}
# _value in {Intersection[float] | Intersection[int] | Intersection[str]}
for _value in float_int_str.values(): ...
# _value in {Intersection[float] | Intersection[int] | Intersection[str]}

# alternatively, you can use Intersection.cast(type, *intersections)
_float : float = Intersection.cast(float, float_int_str)
# maybe we can also support Intersection.cast(tuple[type], *intersections)

# partially-resolved products return an intersection
float_int : Intersection[float|int] = float_int_str[float|int] 
# float_int == Intersection(5, 0.5)

bool_float : Intersection[bool | float] = Intersection(False, 1.0)
bool_int : Intersection[bool | int] = Intersection(True, 42)

# intersection operator is associative but not commutative (right takes precedence)
# also, A & B is syntactic sugar for Intersection(A,B)
float_int_bool = (float_int & bool_int) & bool_float
# float_int_bool == Intersection(False, 42, 1.0)
float_int_bool == float_int & (bool_int & bool_float)
float_int_bool == Intersection((float_int & bool_int), bool_float)
float_int_bool == Intersection(float_int, bool_int, bool_float)
#
#
#

#
# bonus possibilities in the future
#
# set difference with types; not sure how you could narrow this to the static checker though ...
# getting this to work at runtime is easy enough
float_int : Intersection[float | int] = float_int_bool / bool
#
#
#