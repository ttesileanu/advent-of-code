#! /usr/bin/env python
from typing import List

with open("input8.txt", "rt") as f:
    heights = []
    for line in f:
        line = line.strip()
        if len(line) > 0:
            heights.append([int(_) for _ in line])

        if len(heights) > 1:
            assert len(heights[-1]) == len(heights[0])


def partial_max(heights: List[List[int]], edge: str) -> List[List[int]]:
    """Find maximum height from the given edge."""
    m = len(heights)
    n = len(heights[0])

    res = [n * [0] for _ in heights]

    if edge in ["top", "bottom"]:
        k1 = n
        k2 = m
    elif edge in ["left", "right"]:
        k1 = m
        k2 = n
    else:
        raise ValueError(f"unknown edge, {edge}")

    for i1 in range(k1):
        crt_max = -1
        for i2 in range(k2):
            if edge == "top":
                i = i2
                j = i1
            elif edge == "bottom":
                i = m - i2 - 1
                j = i1
            elif edge == "left":
                i = i1
                j = i2
            elif edge == "right":
                i = i1
                j = n - i2 - 1

            res[i][j] = crt_max

            height = heights[i][j]
            crt_max = max(crt_max, height)

    return res


m = len(heights)
n = len(heights[0])

visible = [n * [False] for _ in heights]

for edge in ["left", "right", "bottom", "top"]:
    crt_partial_max = partial_max(heights, edge)
    for i in range(m):
        for j in range(n):
            visible[i][j] = visible[i][j] or (heights[i][j] > crt_partial_max[i][j])

# for i in range(m):
#     print([1 if _ else 0 for _ in visible[i]])

total = sum(sum(1 if _ else 0 for _ in visible[i]) for i in range(m))
print(f"the map is {m} x {n}")
print(f"total number of visible trees: {total}")
