#! /usr/bin/env python
from typing import Tuple

m = 6
n = 40
screen = [n * [" "] for _ in range(m)]


def get_char(j: int, x: int) -> str:
    return "#" if abs(x - j) <= 1 else "."


def advance(i: int, j: int) -> Tuple[int, int]:
    assert i < m
    j += 1
    if j >= n:
        j = 0
        i += 1

    return i, j


with open("input10.txt", "rt") as f:
    x = 1
    i = 0
    j = 0
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        screen[i][j] = get_char(j, x)
        i, j = advance(i, j)
        if line == "noop":
            continue

        assert line.startswith("addx ")
        screen[i][j] = get_char(j, x)
        i, j = advance(i, j)
        value = int(line[5:])

        x += value

for row in screen:
    print("".join(row))
    assert all(_ != " " for _ in row)
