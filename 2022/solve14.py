#! /usr/bin/env python
import sys
import math
from typing import Tuple


def parse_point(s: str) -> Tuple[int, int]:
    b_str, a_str, *_ = s.split(",")
    assert len(_) == 0

    return int(a_str), int(b_str)

origin = (0, 500)

fname = "input14" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    segments = []
    rows = [origin[0], origin[0]]
    cols = [origin[1], origin[1]]
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        points_str = [_.strip() for _ in line.split("->")]
        points = list(map(parse_point, points_str))

        for point in points:
            rows[0] = min(rows[0], point[0])
            rows[1] = max(rows[1], point[0])
            
            cols[0] = min(cols[0], point[1])
            cols[1] = max(cols[1], point[1])

        for start, end in zip(points, points[1:]):
            segments.append((start, end))

n_rows = rows[1] - rows[0] + 1
n_cols = cols[1] - cols[0] + 1

state = [n_cols * ["."] for _ in range(n_rows)]

for start, end in segments:
    if start[0] == end[0]:
        # horizontal
        k0 = min(start[1], end[1])
        k1 = max(start[1], end[1])
        for k in range(k0, k1 + 1):
            state[start[0] - rows[0]][k - cols[0]] = "#"
    elif start[1] == end[1]:
        # vertical
        k0 = min(start[0], end[0])
        k1 = max(start[0], end[0])
        for k in range(k0, k1 + 1):
            state[k - rows[0]][start[1] - cols[0]] = "#"
    else:
        raise ValueError("found segment that is neither horizontal nor vertical")

count = 0
rest = True
while rest:
    # drop a unit of sand!
    assert state[origin[0] - rows[0]][origin[1] - cols[0]] == "."

    ci = origin[0] - rows[0]
    cj = origin[1] - cols[0]
    rest = False
    while ci >= 0 and ci < n_rows and cj >= 0 and cj < n_cols:
        if ci + 1 == n_rows or state[ci + 1][cj] == ".":
            ci += 1
        elif cj == 0 or state[ci + 1][cj - 1] == ".":
            ci += 1
            cj -= 1
        elif cj + 1 == n_cols or state[ci + 1][cj + 1] == ".":
            ci += 1
            cj += 1
        else:
            # we stop here!
            state[ci][cj] = "o"
            rest = True
            break
    
    if rest:
        count += 1

state[origin[0] - rows[0]][origin[1] - cols[0]] = "+"
for row in state:
    print("".join(row))

print(f"number of units of sand that came to rest: {count}")
