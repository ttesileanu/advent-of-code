#! /usr/bin/env python
from dataclasses import dataclass
from typing import Union, Tuple


@dataclass
class Substring:
    s: str = ""
    start: int = 0
    end: int = 0


def grab_first(s: Substring) -> Tuple[Substring, Substring]:
    n_open = 0
    idx = s.start
    while idx < s.end:
        if s.s[idx] == "[":
            n_open += 1
        elif s.s[idx] == "]":
            n_open -= 1
            assert n_open >= 0
        elif n_open == 0 and s.s[idx] == ",":
            break

        idx += 1

    first = Substring(s.s, s.start, idx)
    rest = Substring(s.s, idx + (1 if idx < s.end else 0), s.end)

    assert first.end >= first.start
    assert rest.end >= rest.start
    return first, rest


def compare(s1: Union[str, Substring], s2: Union[str, Substring]) -> int:
    """Return 1 if s1 is lower than s2, -1 if s2 is lower than s1, 0 otherwise."""
    if not hasattr(s1, "start"):
        s1 = Substring(s1, 0, len(s1))
    if not hasattr(s2, "start"):
        s2 = Substring(s2, 0, len(s2))

    ch1 = s1.s[s1.start]
    ch2 = s2.s[s2.start]
    if ch1 == "[" or ch2 == "[":
        # we do a list comparison
        if ch1 == "[":
            # get rid of the parentheses
            s1.start += 1
            s1.end -= 1
            assert s1.end >= s1.start
        if ch2 == "[":
            # get rid of the parentheses
            s2.start += 1
            s2.end -= 1
            assert s2.end >= s2.start

        while True:
            if s1.start == s1.end:
                # first list empty!
                return 1 if s2.end > s2.start else 0
            elif s2.start == s2.end:
                # second list empty while first one is not!
                return -1

            first1, rest1 = grab_first(s1)
            first2, rest2 = grab_first(s2)

            comp = compare(first1, first2)
            if comp == 1:
                return 1
            elif comp == -1:
                return -1
            else:
                s1 = rest1
                s2 = rest2
    else:
        # we compare integers
        assert s1.end > s1.start, s1
        assert s2.end > s2.start, s2
        i1 = int(s1.s[s1.start : s1.end])
        i2 = int(s2.s[s2.start : s2.end])
        if i1 < i2:
            return 1
        elif i1 > i2:
            return -1
        else:
            return 0


with open("input13.txt", "rt") as f:
    idx = 1
    right_order = []
    while True:
        try:
            line1 = next(f)
        except StopIteration:
            break

        line2 = next(f)
        try:
            _ = next(f)
        except StopIteration:
            _ = ""
        assert len(_.strip()) == 0

        line1 = line1.strip()
        line2 = line2.strip()

        if compare(line1, line2) == 1:
            right_order.append(idx)

        idx += 1

print(f"there are {len(right_order)} pairs in correct order:")
print(right_order)
print()
print(f"sum of indices of pairs in right order: {sum(right_order)}")
