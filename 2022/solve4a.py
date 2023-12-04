#! /usr/bin/env python
import os
from typing import Tuple


def parse(s: str) -> Tuple[int, int]:
    start, stop, *_ = s.split("-")
    assert len(_) == 0

    return int(start), int(stop)


with open("input4.txt", "rt") as f:
    count = 0
    for line in f:
        s_range1, s_range2, *_ = line.split(",")
        assert len(_) == 0

        range1 = parse(s_range1)
        range2 = parse(s_range2)

        if range2[0] <= range1[1] and range2[1] >= range1[0]:
            count += 1

print(f"Total number of overlapping pairs: {count}")
