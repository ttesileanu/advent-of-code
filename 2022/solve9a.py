#! /usr/bin/env python
from typing import List

with open("input9.txt", "rt") as f:
    length = 10

    knots = [[0, 0] for _ in range(length)]

    tail_locations = set()
    tail_locations.add(tuple(knots[-1]))
    for line in f:    
        line = line.strip()
        if len(line) == 0:
            continue

        direction, count_str, *_ = line.split(" ")
        assert len(_) == 0
        assert direction in "LRUD"

        count = int(count_str)
        assert count > 0

        for i in range(count):
            if direction == "L":
                knots[0][1] -= 1
            elif direction == "R":
                knots[0][1] += 1
            elif direction == "U":
                knots[0][0] -= 1
            else:  # direction == "D":
                knots[0][0] += 1

            for k in range(1, length):
                lead = knots[k - 1]
                follow = knots[k]

                if abs(follow[0] - lead[0]) > 1 or abs(follow[1] - lead[1]) > 1:
                    # need to move tail
                    if abs(follow[1] - lead[1]) < 2:
                        follow[1] = lead[1]
                        follow[0] = (lead[0] + follow[0]) // 2
                    elif abs(follow[0] - lead[0]) < 2:
                        follow[0] = lead[0]
                        follow[1] = (lead[1] + follow[1]) // 2
                    else:
                        follow[0] = (lead[0] + follow[0]) // 2
                        follow[1] = (lead[1] + follow[1]) // 2
                        
            tail_locations.add(tuple(knots[-1]))
            
min_row = max_row = knots[0][0]
min_col = max_col = knots[0][1]
for loc in tail_locations:
    min_row = min(min_row, loc[0])
    max_row = max(max_row, loc[0])
    min_col = min(min_col, loc[1])
    max_col = max(max_col, loc[1])
    
for loc in knots:
    min_row = min(min_row, loc[0])
    max_row = max(max_row, loc[0])
    min_col = min(min_col, loc[1])
    max_col = max(max_col, loc[1])

print(min_row, max_row, min_col, max_col)

n_rows = max_row - min_row + 1
n_cols = max_col - min_col + 1
matrix = [n_cols * ["."] for _ in range(n_rows)]
# for loc in tail_locations:
#     matrix[loc[0] - min_row][loc[1] - min_col] = "#"

for i, loc in enumerate(knots[::-1]):
    matrix[loc[0] - min_row][loc[1] - min_col] = str(length - i - 1)

for row in matrix:
    print("".join(row))

print(f"the tail visited {len(tail_locations)} positions")
