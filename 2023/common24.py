from dataclasses import dataclass
from typing import Generic, Iterator, List, Sequence, Tuple, TypeVar, Union

T = TypeVar("T")


class Array(Generic[T]):
    contents: List[T]

    def __init__(self, a: Sequence[T]):
        self.contents = list(a)

    def __repr__(self) -> str:
        s = "Array("
        s += "[" + ", ".join(str(_) for _ in self.contents)
        s += "]"
        s += ")"
        return s

    def __len__(self) -> int:
        return len(self.contents)

    def __getitem__(self, _: int) -> T: ...

    def __getitem__(self, _: slice) -> "Array[T]": ...

    def __getitem__(self, idx: Union[int, slice]) -> Union[T, "Array[T]"]:
        if isinstance(idx, slice):
            return Array(self.contents[idx])
        else:
            return self.contents[idx]

    def __setitem__(self, idx: Union[int, slice], value: Union[T, Sequence[T]]):
        if isinstance(idx, slice):
            if hasattr(value, "__len__"):
                self.contents[idx] = value
            else:
                start = slice.start if slice.start is not None else 0
                stop = slice.stop if slice.stop is not None else len(self.contents)
                assert start >= 0 and stop >= 0

                start = min(start, len(self.contents))
                stop = min(stop, len(self.contents))
                l = stop - start
                if l != len(value):
                    raise IndexError(
                        f"Trying to set {l} elements using a {len(value)}-element array"
                    )

                for i in range(start, stop):
                    self.contents[i] = value[i]
        else:
            self.contents[idx] = value[idx]

    def __iter__(self) -> Iterator[T]:
        return iter(self.contents)

    def __eq__(self, other: Union[T, Sequence[T]]) -> "Array[bool]":
        if hasattr(other, "__len__"):
            self._check_shape(other, "check for equality")
            return Array([x == y for x, y in zip(self.contents, other)])
        else:
            return Array([x == other for x in self.contents])

    def __add__(self, other: Sequence[T]) -> "Array[T]":
        self._check_shape(other, "add")
        return Array([x + y for x, y in zip(self.contents, other)])

    def __sub__(self, other: Sequence[T]) -> "Array[T]":
        self._check_shape(other, "subtract")
        return Array([x - y for x, y in zip(self.contents, other)])

    def __mul__(self, scalar: T) -> "Array[T]":
        return Array([scalar * x for x in self.contents])

    def __rmul__(self, scalar: T) -> "Array[T]":
        return Array([scalar * x for x in self.contents])

    def __truediv__(self, scalar: T) -> "Array[T]":
        return Array([x / scalar for x in self.contents])

    def __floordiv__(self, scalar: T) -> "Array[T]":
        return Array([x // scalar for x in self.contents])

    def __mod__(self, scalar: T) -> "Array[T]":
        return Array([x % scalar for x in self.contents])

    def __pow__(self, scalar: T) -> "Array[T]":
        return Array([x**scalar for x in self.contents])

    def __neg__(self) -> "Array[T]":
        return Array([-x for x in self.contents])

    def __pos__(self) -> "Array[T]":
        return Array([+x for x in self.contents])

    def _check_shape(self, other: Sequence[T], op: str):
        if len(self) != len(other):
            raise ValueError(
                f"Cannot {op} incompatible shapes {self.shape}, {shape(other)}"
            )


def shape(seq: Sequence[T]) -> Tuple[int, ...]:
    return (len(seq),)


@dataclass
class Hailstone:
    position: Array[int]
    velocity: Array[int]
