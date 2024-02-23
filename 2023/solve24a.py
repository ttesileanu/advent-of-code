#! /usr/bin/env python
from dataclasses import dataclass
from fractions import Fraction
from typing import Generic, Iterator, List, Optional, Sequence, Tuple, TypeVar, Union

from utils import iterinput, logger


BOUNDS = [200_000_000_000_000, 400_000_000_000_000]


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
            return Array([x == y] for x, y in zip(self.contents, other))
        else:
            return Array([x == other] for x in self.contents)

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


def intersect2d_fwd(
    stone1: Hailstone, stone2: Hailstone, check_bounds: bool = True
) -> Optional[Array]:
    # ignoring z coordinate and looking only at positive times
    # x = p1 + t1 * v1 = p2 + t2 * v2
    #    -> v1 * t1 - v2 * t2 = p2 - p1
    # In matrix form:
    #   [ v1x   -v2x ] [ t1 ]    [ p2x - p1x ]
    #   [ v1y   -v2y ] [ t2 ]  = [ p2y - p1y ]

    logger.debug(f"A: {stone1}")
    logger.debug(f"B: {stone2}")

    v1x, v1y, _ = stone1.velocity
    v2x, v2y, _ = stone2.velocity
    dpx = stone2.position[0] - stone1.position[0]
    dpy = stone2.position[1] - stone1.position[1]

    det = v1y * v2x - v1x * v2y
    det1 = dpy * v2x - dpx * v2y
    det2 = v1x * dpy - v1y * dpx
    if det != 0:
        # unique solution
        t1 = Fraction(det1, det)
        t2 = Fraction(det2, det)
        if t1 < 0 or t2 < 0:
            if t1 < 0 and t2 < 0:
                logger.debug("    Paths crossed in the past for both hailstones.")
            elif t1 < 0:
                logger.debug("    Paths crossed in the past for both hailstone A.")
            else:
                logger.debug("    Paths crossed in the past for both hailstone B.")
            return None
        else:
            cross1 = stone1.position[:2] + t1 * stone1.velocity[:2]
            cross2 = stone2.position[:2] + t2 * stone2.velocity[:2]
            assert all(cross1 == cross2)

            if check_bounds:
                is_inside = all(BOUNDS[0] <= _ <= BOUNDS[1] for _ in cross1)
                inside_str = ["out", "in"][is_inside] + "side"

                logger.debug(f"    Paths will cross {inside_str} test area.")
                return cross1 if is_inside else None
            else:
                logger.debug("    Paths will cross. (no bounds check, by request)")
                return cross1
    else:
        if det1 != 0 or det2 != 0:
            # no solution
            logger.debug("    Paths are parallel; they never intersect.")
        else:
            raise NotImplementedError(
                "Hailstones with identical trajectories not supported"
            )


if __name__ == "__main__":
    hailstones = []
    for line in iterinput():
        pos_str, vel_str = line.split("@")
        pos = [int(_) for _ in pos_str.split(",", maxsplit=2)]
        vel = [int(_) for _ in vel_str.split(",", maxsplit=2)]

        hailstones.append(Hailstone(Array(pos), Array(vel)))

    n = len(hailstones)
    logger.info(f"There are {len(hailstones)} hailstones.")
    logger.debug(f"{hailstones=}")

    count = 0
    for i in range(n):
        stone1 = hailstones[i]
        for j in range(i + 1, n):
            stone2 = hailstones[j]
            x = intersect2d_fwd(stone1, stone2)
            if x is not None:
                count += 1

    print(f"There are {count} intersection in test area.")
