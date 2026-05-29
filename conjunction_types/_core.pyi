from __future__ import annotations

from typing import Any, Iterator, overload

type ConjOrT[T] = Conjunction[T] | T

class ConjunctionMeta[ItemTs](type):
    @overload
    def __getitem__[T](cls, item: type[Conjunction[T]]) -> type[Conjunction[T]]: ...
    @overload
    def __getitem__[T](cls, item: Conjunction[T]) -> type[Conjunction[T]]: ...
    @overload
    def __getitem__[T](cls, item: T) -> type[Conjunction[T]]: ...
    def __eq__(cls, other: Any) -> bool: ...
    def __hash__(cls) -> int: ...
    def __contains__(cls, item: object) -> bool: ...
    def __iter__(cls) -> Iterator[type]: ...
    def __len__(cls) -> int: ...
    def __repr__(cls) -> str: ...
    @overload
    def __and__[I, T](cls: type[Conjunction[I]], other: type[Conjunction[T]]) -> type[Conjunction[I | T]]: ...
    @overload
    def __and__[I, T](cls: type[Conjunction[I]], other: type[T]) -> type[Conjunction[I | T]]: ...
    @overload
    def __rand__[I, T](cls: type[Conjunction[I]], other: type[Conjunction[T]]) -> type[Conjunction[I | T]]: ...
    @overload
    def __rand__[I, T](cls: type[Conjunction[I]], other: type[T]) -> type[Conjunction[I | T]]: ...
    def __instancecheck__(cls, instance: Any) -> bool: ...
    def __subclasscheck__(cls, subclass: Any) -> bool: ...

class Conjunction[ItemTs](metaclass=ConjunctionMeta):
    @property
    def _typing_items(self) -> ItemTs: ...
    @overload
    def __new__[T1](cls, v1: Conjunction[T1]) -> Conjunction[T1]: ...
    @overload
    def __new__[T1](cls, v1: T1) -> Conjunction[T1]: ...
    @overload
    def __new__[T1, T2](cls, v1: Conjunction[T1], v2: Conjunction[T2]) -> Conjunction[T1 | T2]: ...
    @overload
    def __new__[T1, T2](cls, v1: Conjunction[T1], v2: T2) -> Conjunction[T1 | T2]: ...
    @overload
    def __new__[T1, T2](cls, v1: T1, v2: Conjunction[T2]) -> Conjunction[T1 | T2]: ...
    @overload
    def __new__[T1, T2](cls, v1: ConjOrT[T1], v2: ConjOrT[T2]) -> Conjunction[T1 | T2]: ...
    @overload
    def __new__[T1, T2, T3](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
    ) -> Conjunction[T1 | T2 | T3]: ...
    @overload
    def __new__[T1, T2, T3, T4](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
    ) -> Conjunction[T1 | T2 | T3 | T4]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
        v11: ConjOrT[T11],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
        v11: ConjOrT[T11],
        v12: ConjOrT[T12],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
        v11: ConjOrT[T11],
        v12: ConjOrT[T12],
        v13: ConjOrT[T13],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
        v11: ConjOrT[T11],
        v12: ConjOrT[T12],
        v13: ConjOrT[T13],
        v14: ConjOrT[T14],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13 | T14]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
        v11: ConjOrT[T11],
        v12: ConjOrT[T12],
        v13: ConjOrT[T13],
        v14: ConjOrT[T14],
        v15: ConjOrT[T15],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13 | T14 | T15]: ...
    @overload
    def __new__[T1, T2, T3, T4, T5, T6, T7, T8, T9, T10, T11, T12, T13, T14, T15, T16](
        cls,
        v1: ConjOrT[T1],
        v2: ConjOrT[T2],
        v3: ConjOrT[T3],
        v4: ConjOrT[T4],
        v5: ConjOrT[T5],
        v6: ConjOrT[T6],
        v7: ConjOrT[T7],
        v8: ConjOrT[T8],
        v9: ConjOrT[T9],
        v10: ConjOrT[T10],
        v11: ConjOrT[T11],
        v12: ConjOrT[T12],
        v13: ConjOrT[T13],
        v14: ConjOrT[T14],
        v15: ConjOrT[T15],
        v16: ConjOrT[T16],
    ) -> Conjunction[T1 | T2 | T3 | T4 | T5 | T6 | T7 | T8 | T9 | T10 | T11 | T12 | T13 | T14 | T15 | T16]: ...
    @overload
    def __new__(cls, *values: Any) -> Conjunction[Any]: ...
    def __init__(self, *values: Any, **kwargs: Any) -> None: ...
    def __setattr__(self, name: str, value: Any) -> None: ...
    def __delattr__(self, name: str) -> None: ...
    @classmethod
    @overload
    def __class_getitem__[T](cls, item: type[Conjunction[T]]) -> type[Conjunction[T]]: ...
    @classmethod
    @overload
    def __class_getitem__[T](cls, item: Conjunction[T]) -> type[Conjunction[T]]: ...
    @classmethod
    @overload
    def __class_getitem__[T](cls, item: T) -> type[Conjunction[T]]: ...
    @overload
    def __getitem__[T](self, types: type[T]) -> Conjunction[T]: ...
    @overload
    def __getitem__[T](self, types: T) -> Conjunction[T]: ...
    def __contains__(self, item: object) -> bool: ...
    def __iter__(self) -> Iterator[type[ItemTs]]: ...
    def keys(self) -> Iterator[type[ItemTs]]: ...
    def values(self) -> Iterator[Conjunction[ItemTs]]: ...
    def items(self) -> Iterator[tuple[type[ItemTs], Conjunction[ItemTs]]]: ...
    def to[ItemT](self, typ: type[ItemT]) -> ItemT: ...
    @overload
    def __and__[T](self, other: Conjunction[T]) -> Conjunction[ItemTs | T]: ...
    @overload
    def __and__[T](self, other: T) -> Conjunction[ItemTs | T]: ...
    @overload
    def __rand__[T](self, other: Conjunction[T]) -> Conjunction[ItemTs | T]: ...
    @overload
    def __rand__[T](self, other: T) -> Conjunction[ItemTs | T]: ...
    def __truediv__(self, types: object) -> Conjunction[Any]: ...
    def __eq__(self, other: Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __repr__(self) -> str: ...
    def __len__(self) -> int: ...
