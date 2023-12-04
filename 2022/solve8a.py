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


def view_distance(heights: List[List[int]], direction: str) -> List[List[int]]:
    """Calculate view distance in the given direction."""
    m = len(heights)
    n = len(heights[0])

    res = [n * [0] for _ in heights]

    assert direction in ["up", "down", "left", "right"]
    for i in range(m):
        for j in range(n):
            height = heights[i][j]

            idx = i if direction in ["up", "down"] else j
            step = -1 if direction in ["left", "up"] else 1

            idx += step
            count = m if direction in ["up", "down"] else n
            distance = 0
            while idx >= 0 and idx < count:
                distance += 1

                if direction in ["up", "down"]:
                    i1 = idx
                    i2 = j
                else:
                    i1 = i
                    i2 = idx

                obstacle = heights[i1][i2]
                if obstacle >= height:
                    break

                idx += step

            res[i][j] = distance

    return res


distances = {
    direction: view_distance(heights, direction)
    for direction in ["up", "down", "left", "right"]
}

m = len(heights)
n = len(heights[0])

scores = [n * [1] for _ in heights]

for i in range(m):
    for j in range(n):
        for distance_map in distances.values():
            scores[i][j] *= distance_map[i][j]

# for i in range(m):
#     print(scores[i])

max_score = max(max(_) for _ in scores)
print(f"maximum scenic score is {max_score}")
