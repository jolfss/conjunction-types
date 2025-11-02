# Conjunction Types

A pragmatic compromise for intersection-like semantics in Python with hints.

[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`Conjunction[A | B | C]` represents a container holding exactly one value of each type `A`, `B`, and `C`.

```python
from conjunction_types import Conjunction

# Type construction: | inside Conjunction[...] declares member types
UserData = Conjunction[int | str | dict[str, str]]
Credentials = Conjunction[str | dict[str, str]]

# Type operations: subset checking (covariant)
assert int in UserData                     # type membership
assert Credentials in UserData             # Credentials <: UserData
assert UserData not in Credentials         # not a subset

# Type combination: & operator merges Conjunction types (type-level, commutative)
Combined = Conjunction[int | str] & Conjunction[float | bool]
assert Combined == Conjunction[int | str | float | bool]

# Value construction: infer types from arguments
user = Conjunction(42, "alice", {"role": "admin"})
profile = Conjunction("bob", {"status": "active"})

# Value composition: & merges instances (right-precedence for overlapping types; warning emitted)
merged = user & profile
assert int in merged                       # from user
assert str in merged                       # both had str; profile's wins
assert dict[str, str] in merged            # both had dict; profile's wins

# Subscript indexing: extract subset of types
partial: Conjunction[int | str] = merged[int | str]
assert int in partial and str in partial
assert dict not in partial                 # dict was excluded

# Operations preserve type structure
data1 = Conjunction(1, "x") & Conjunction(2.0)
data2 = Conjunction(1, "y", 3.0)
assert (data1 & data2)[int | float] == Conjunction(1, 3.0)[int | float]

# Type equality: permutation-invariant
assert Conjunction[int | str] == Conjunction[str | int]
assert Conjunction(1, "a") != Conjunction("a", 1)  # values differ
```

## Installation

```bash
pip install conjunction-types
```

## Conceptual Foundations

`Conjunction` is a **type-indexed product** that enables intersection-like behavior through explicit projection.

### Intersection Types (via projection)

In formal type theory, an intersection type `A ∧ B` is a value that is *simultaneously* `A` and `B` with subtyping `A ∧ B <: A` and `A ∧ B <: B`. Python cannot express such multiple-inheritance-of-instance semantics in a way usable to the type checkers.

`Conjunction` provides **projection-based intersection semantics** instead:

```python
# Traditional intersection: cannot be spelled in Python typing today
# x: A & B  # would be both A and B simultaneously

# Conjunction approach: separate storage, type-safe extraction
c: Conjunction[A | B] = Conjunction(a_instance, b_instance)

# Projection yields true instances of the requested type
x: A = c.to(A)  # ✅ type: A
y: B = c.to(B)  # ✅ type: B

# Semantic law: projection is defined iff the type is present
# Conjunction[T1 | ... | Tn].to(T') <: T'  ⇔  T' ∈ {T1, ..., Tn}

# Subtyping does not hold at the base types:
issubclass(Conjunction[A | B], A)  # ❌ False
issubclass(Conjunction[A | B], B)  # ❌ False

# But subset relations hold among Conjunction types:
AB = Conjunction[int | str]
ABC = Conjunction[int | str | float]
assert issubclass(AB, ABC)  # ✅ AB <: ABC
```

This mirrors intersection semantics **at use sites** as long as contained objects are **state-disjoint** (no shared mutable state). Broadcasting writes across all members (by intercepting `__setattr__`) is theoretically possible but intentionally omitted due to MRO complexity and low practical gain. In fact, this probably indicates that you really want a new type that groups the shared state together.

### Product Types (true at runtime)

`Conjunction[A | B | C]` is a **real product**: it stores one value per member type, behaving like a type-indexed map `{type → instance}`.

```python
# Conceptually: Conjunction[A | B | C] ≅ (a: A, b: B, c: C)

# Type-indexed vs position-indexed
pair = (42, "hello")                  # positional
bag  = Conjunction(42, "hello")       # type-indexed: bag.to(int) == 42

# Type uniqueness: cannot represent (int, int)
# Distinct parametric types *are* allowed
c = Conjunction({"a": 1}, {"b": "x"})  # dict[str,int] + dict[str,str]
xi: dict[str, int] = c.to(dict[str, int])
xs: dict[str, str] = c.to(dict[str, str])
```

### Algebraic Properties

> There are **two levels** to keep straight:
>
> * **Type level**: combining `Conjunction[...]` types.
> * **Value level**: merging runtime instances with `&`.

| Property        | Type level | Value level | Notes                                                                                 |
| :-------------- | :--------: | :---------: | :------------------------------------------------------------------------------------ |
| **Associative** |      ✅     |      ✅      | `(A & B) & C == A & (B & C)`                                                          |
| **Commutative** |      ✅     |      ❌      | Type-level `&` is set-like; value-level `&` is right-precedence for overlapping types |
| **Idempotent**  |      ✅     |      ✅      | Duplicates are flattened; merging same type keeps right-hand value                    |
| **Identity**    |      ✅     |      ✅      | `Conjunction[]` is identity for `&`                                                   |

```python
# Associativity
c1 = Conjunction(1, "a")
c2 = Conjunction(2.0, True)
c3 = Conjunction([], {})
assert (c1 & c2) & c3 == c1 & (c2 & c3)

# Non-commutativity at value level (right side wins on conflict)
x = Conjunction(42, "first")
y = Conjunction(99, "second")
z = x & y
assert z.to(int) == 99
assert z.to(str) == "second"
```

### Operator Semantics (the `|` and `&` "trick")

* **Inside `Conjunction[...]`**, the `|` operator *lists member types*. Although `|` means union in Python, here it’s used to declare the **conjunctive product’s index set**.
* **At the type level**, `&` combines two `Conjunction[...]` types by taking the union of their member sets. This is **commutative** and **associative**.
* **At the value level**, `&` merges two instances. This is **associative** but **not commutative**; on overlapping types, the **right-hand** instance’s value wins.
* `[]` (subscription) selects a subset **at the type level** and returns a new `Conjunction[...]` of that subset.
* `/` removes types (set difference) at the value level.

```python
# Type level
AB   = Conjunction[int | str]
BC   = Conjunction[str | bool]
ABBC = AB & BC
assert ABBC == Conjunction[int | str | bool]

# Value level
v = Conjunction(1, "x") & Conjunction("y")
assert v.to(str) == "y"  # right-precedence on str

# Subselection and difference
sub: Conjunction[int] = v[int]
v2 = v / str
assert str not in v2
```

---

## API Reference (selected)

### Type Construction

```python
UserID = Conjunction[int]
UserProfile = Conjunction[int | str | dict[str, str]]

# Subset checking (covariant)
assert int in UserProfile
assert UserID in UserProfile  # Conjunction[int] <: Conjunction[int|str|dict]

# Type equivalence (permutation invariant)
assert Conjunction[int | str] == Conjunction[str | int]

# Generic types are distinguished
IntMap = Conjunction[dict[str, int]]
StrMap = Conjunction[dict[str, str]]
assert IntMap != StrMap
```

### Instance Construction & Composition

```python
c = Conjunction(42, "hello", 3.14)
assert {int, str, float} <= set(c)

# Compose existing conjunctions
c1 = Conjunction(42, "alice")
c2 = Conjunction({"role": "admin"})
merged = c1 & c2  # Conjunction[int | str | dict]

# Right-precedence on overlaps
x = Conjunction(1, "first")
y = Conjunction(2, "second")
z = x & y
assert z.to(int) == 2 and z.to(str) == "second"
```

### Extraction & Slicing

```python
c = Conjunction(42, "hello", 3.14)

# Single value extraction (type-safe)
value: int = c.to(int)

# Partial extraction (returns Conjunction)
sub: Conjunction[int | str] = c[int | str]
assert float not in sub and sub.to(int) == 42

# Membership testing (types or Conjunction types)
assert int in c
assert (int | str) in c
assert not ((int | bool) in c)
```

### Set-Like Operations

```python
c = Conjunction(42, "hello", 3.14, True)

# Remove types via /
c2 = c / str                # Remove str
c3 = c / (str | bool)       # Remove str and bool

assert int in c2 and float in c2 and str not in c2
```

### Properties

```python
c = Conjunction(42, "hello", 3.14)

# Immutable
try:
    c.field = "value"
except TypeError:
    pass

# Hashable
s = {c}
d = {c: "metadata"}

# Iterate types / values
for typ in c:
    print(typ)
for typ, wrapped in c.items():
    assert wrapped.to(typ) is not None
```



---

## Advanced (Theory): Monadic Lifting over Conjunctions

> **Status:** not implemented; this section documents a design direction.

`Conjunction` already acts as a *context* that can hold auxiliary state alongside a base type. This suggests a path to **monadic lifting**, where we pair each base type with a monadic carrier and wire `.to()` to honor monadic laws.

### Idea: pair a type with a monadic state

Consider `Conjunction[T | M[T]]`, where `M` is a monad (e.g., `Optional`, `Result[E, _]`, or an application-specific effect type). We could provide combinators that:

* Lift a pure function `f: T → U` to act on the `T`-component and transport effects via the `M[T]` component.
* Define `bind`/`flat_map` that sequences effects by updating `M[T]` and switching focus to `M[U]`.

Sketch of potential API (illustrative only):

```python
from typing import TypeVar, Callable

T = TypeVar("T")
U = TypeVar("U")

# Hypothetical helper signatures
# (details depend on the chosen monad interface)

def fmap(c: Conjunction[T | M[T]], f: Callable[[T], U]) -> Conjunction[U | M[U]]: ...

def bind(c: Conjunction[T | M[T]], f: Callable[[T], Conjunction[U | M[U]]]) -> Conjunction[U | M[U]]: ...

# And: projection stays type-safe
u: U = fmap(c, f).to(U)
```

**Why `.to()` matters:** If `M` hooks into `.to()`, the projection point becomes the natural boundary where effects are interpreted or realized, keeping the product-at-rest / projection-at-use discipline.

### Practical notes

* You likely want a *uniform* monad protocol (e.g., `map`, `flat_map`) to avoid hard-coding special cases.
* Laws (identity, associativity) can be tested using property-based tests on the `&` and `.to()` interplay.
* This design remains compatible with the current semantics: it *extends* them rather than changing them.

---

## Advanced (Theory): Monadic and Conjunction-Aware Abstractions

> **Status:** not implemented; this section documents a unified design direction combining Monads, a `@conj` decorator, and Ellipsis-based late casting.

`Conjunction` already acts as a *context* that can hold auxiliary state alongside base types. This naturally suggests extending the concept into **monadic lifting**, where each base type is paired with a state carrier, and functions can automatically interact with both ordinary and monadic conjunctions through a decorator.

### 1. Concept: Monadic Conjunctions

Define a type constructor `MyMonad[T] : Conjunction[T | MyMonadState[T]]`, where `MyMonadState[T]` tracks contextual information (e.g., logging, tracing, dependency injection state). The `MyMonad` class can **override `.to(...)`** to store or modify the associated `MyMonadState` before projecting the requested type.

```python
class MyMonad[T](Conjunction[T | MyMonadState[T]]):
    def to[U](self, typ: type[U]) -> U:
        state = self.to(MyMonadState[T])
        state.before_access(typ)  # custom hook
        value = super().to(typ)
        state.after_access(typ, value)
        return value
```

Here, `.to()` becomes the **natural effect boundary** — where side effects are realized, logs are updated, or transactional state transitions occur.

### 2. The `@conj` Decorator: Conjunction-Aware Function Calls

The `@conj` decorator makes functions automatically *conjunction-aware*, allowing them to receive a `Conjunction[...]` or a derived monadic variant (like `MyMonad[...]`) in place of individual parameters.

#### Semantics

When a decorated function is called:

1. The decorator inspects the function’s annotations.
2. If the argument is a `Conjunction[...]`, it projects each annotated parameter type using `.to(T)`.
3. The function is invoked with those projected values.
4. If a parameter type is missing, a `TypeError` is raised.
5. If the arguments are plain values, the function executes normally.

This allows seamless invocation of ordinary functions with monadic or conjunction-typed inputs.

```python
@conj
def render(user: str, flags: dict[str, bool]) -> str:
    return f"User {user}, Flags: {flags}"

# Using a monadic conjunction that logs state access
mon = MyMonad("alice", {"dark": True}, MyMonadState())
result = render(mon)  # decorator projects user/flags via monadic .to()
```

The function’s implementation remains unaware of whether the inputs are pure conjunctions or stateful monads — the `@conj` decorator and `.to()` handle the behavior injection transparently.

### 3. Late Casting and Ellipsis Semantics

The decorator could support *late casting* by interpreting `Conjunction[..., A]` as “at least `A`, possibly more.” This allows writing flexible function signatures that can accept conjunctions containing additional context or state.

```python
@conj
def process(data: Conjunction[..., Payload]) -> None:
    payload = data.to(Payload)
    log_state = data.to(MyMonadState[Payload])  # optional side data
    ...
```

Implementing Ellipsis-aware type construction would let conjunctions express **open type sets**, e.g.:

```python
# Open conjunction: any conjunction containing str
Conjunction[..., str]
```

This allows decorators and higher-order functions to express *minimum requirements* rather than exact conjunction signatures.

### 4. Unified Behavior Model

The unified model ties together **monadic lifting**, **decorator-based function adaptation**, and **ellipsis-based polymorphism**:

| Mechanism        | Role                                       | Effect                                         |
| ---------------- | ------------------------------------------ | ---------------------------------------------- |
| `.to(T)`         | Defines monadic effect boundary            | Intercepts access and applies state logic      |
| `@conj`          | Enables automatic projection at call sites | Makes ordinary functions conjunction-aware     |
| `...` (Ellipsis) | Declares open conjunctions                 | Enables partial type matching and late casting |

Together these enable a fully general pattern: **composable conjunction-based effects**.

```python
@conj
def compute(x: int, y: float) -> float:
    return x + y

mon = MyMonad(3, 4.5, MyMonadState())
result = compute(mon)  # automatic extraction + side-effect logging
```

### 5. Design Notes

* The monadic layer extends existing semantics — `.to()` remains the stable API boundary.
* Effects and state propagation are explicit but orthogonal to the value semantics of `Conjunction`.
* The decorator and Ellipsis features can evolve independently; both rely on existing type-indexed lookup.
* A uniform `MonadProtocol` (defining `map`/`flat_map`) could generalize this design across implementations.

This architecture unifies **contextual state**, **intersection-like structure**, and **functional effect semantics** within one coherent framework.

---

## Type Relations Summary

| Concept                   | Relation to `Conjunction` 
| :---                      | :---                     
| **Intersection**          | Imitated under `.to(T)` projection; not a true structural subtype of each member 
| **Product**               | True at runtime (type-indexed Cartesian product over unique keys)                                                                         
| **Coproduct/Sum**         | Under `.to(T)`, this forms a simple sum type (branch for each T).
| **Union (`A\| B`)**       | Syntax reused **inside** `Conjunction[...]` to list member types (index set) 
| **Tuples / Named tuples** | Position-indexed products; `Conjunction` is type-indexed and cannot duplicate a type

---

## Requirements

* Python 3.12+
* Zero runtime dependencies
* Works with static type checkers (Pyright, Pylance, mypy)

## Development

```bash
pip install -e ".[dev]"
pytest -q
pyright
```

## License

MIT License. See [LICENSE](LICENSE) for details.

## Links

* **Repository**: [https://github.com/jolfss/conjunction-types](https://github.com/jolfss/conjunction-types)
* **Issues**: [https://github.com/jolfss/conjunction-types/issues](https://github.com/jolfss/conjunction-types/issues)
* **PyPI**: [https://pypi.org/project/conjunction-types/](https://pypi.org/project/conjunction-types/)