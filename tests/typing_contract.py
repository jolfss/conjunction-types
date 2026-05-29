"""Static typing contract checked with `ty check`."""

from typing import Literal, assert_type

from conjunction_types import Conjunction


class A: ...


class B: ...


class C: ...


class D: ...


class E: ...


class F: ...


class G: ...


class H: ...


class I: ...


class J: ...


class K: ...


class L: ...


class M: ...


class N: ...


class O: ...


class P: ...


Simple = Conjunction[int | str]
simple: type[Conjunction[int | str]] = Simple

Combined = Conjunction[int | str] & Conjunction[float | bool]
combined: type[Conjunction[int | str | float | bool]] = Combined

user: Conjunction[int | str | dict[str, str]] = Conjunction(42, "alice", {"role": "admin"})
profile: Conjunction[str | dict[str, str]] = Conjunction("bob", {"status": "active"})
merged: Conjunction[int | str | dict[str, str]] = user & profile
assert_type(merged, Conjunction[Literal[42, "alice", "bob"] | dict[str, str]])

partial = merged[int]
assert_type(partial, Conjunction[int])

name = merged.to(str)
assert_type(name, str)

wrapped: Conjunction[int | float] = Conjunction(Conjunction(1) & Conjunction(2.0))

wide = Conjunction(A(), B(), C(), D(), E(), F(), G(), H(), I(), J(), K(), L(), M(), N(), O(), P())
assert_type(wide, Conjunction[A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P])
