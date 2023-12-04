#! /usr/bin/env python
import sys
import time
from tqdm import tqdm

from typing import List, Optional


def horizontal(
    x: int, y: int, pit: List[List[str]], action: str, count: int = 4
) -> bool:
    if action == "test":
        for i in range(x, x + count):
            if pit[y][i] != ".":
                # collision!
                return True
    elif action == "place":
        for i in range(x, x + count):
            pit[y][i] = "#"
    else:
        raise ValueError(f"unknown action: {action}")

    return False


def vertical(x: int, y: int, pit: List[List[str]], action: str, count: int = 4) -> bool:
    if action == "test":
        for j in range(y, y + count):
            if pit[j][x] != ".":
                # collision!
                return True
    elif action == "place":
        for j in range(y, y + count):
            pit[j][x] = "#"
    else:
        raise ValueError(f"unknown action: {action}")

    return False


def cross(x: int, y: int, pit: List[List[str]], action: str) -> bool:
    res = horizontal(x, y + 1, pit, action, count=3)
    if not res:
        return vertical(x + 1, y, pit, action, count=3)
    else:
        return True


def ell(x: int, y: int, pit: List[List[str]], action: str) -> bool:
    res = horizontal(x, y, pit, action, count=3)
    if not res:
        return vertical(x + 2, y, pit, action, count=3)
    else:
        return True


def box(x: int, y: int, pit: List[List[str]], action: str) -> bool:
    res = horizontal(x, y, pit, action, count=2)
    if not res:
        return horizontal(x, y + 1, pit, action, count=2)
    else:
        return True


def collision(rock_type: int, x: int, y: int, pit: List[List[str]]) -> bool:
    fct = rock_mapping[rock_type]
    return fct(x, y, pit, action="test")


def place(rock_type: int, x: int, y: int, pit: List[List[str]]):
    fct = rock_mapping[rock_type]
    fct(x, y, pit, action="place")


def show(pit: List[List[str]]):
    print()
    n = len(pit)
    for k in range(n):
        row = pit[n - k - 1]
        print("".join(row))


rock_mapping = [horizontal, cross, ell, vertical, box]

fname = "input17" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    lines = [__ for __ in (_.strip() for _ in f) if len(__) > 0]
    assert len(lines) == 1

    jet = [1 if _ == ">" else -1 for _ in lines[0]]

width = 7
start_x = 2
gap_y = 3

# current level of highest rock in the room, or the floor
bottom = 0
pit = [width * ["#"]]

n_types = 5
rock_type = 0

rock_widths = [4, 3, 3, 1, 2]
rock_heights = [1, 3, 3, 4, 2]

t0 = time.time()

n_rocks = 2022
# n_rocks = 11
jet_idx = 0
for i in range(n_rocks):
#     show(pit)

    cx, cy = start_x, bottom + gap_y + 1

    # make sure we have enough space in our pit
    to_add = cy + rock_heights[rock_type] - len(pit)
    if to_add > 0:
        pit.extend(width * ["."] for _ in range(to_add))

    while True:
        # move horizontally
        old_cx = cx
        cx += jet[jet_idx]
        
#         print(f"from {old_cx}, {cy}, wind pushes {jet[jet_idx]}; ", end="")
        
        jet_idx = (jet_idx + 1) % len(jet)

        # keep within bounds
        if cx < 0:
            cx = old_cx

        if cx + rock_widths[rock_type] > width:
            cx = old_cx


        # did we hit anything?
        if cx != old_cx and collision(rock_type, cx, cy, pit):
            cx = old_cx

        # move vertically
        old_cy = cy
        cy -= 1

        # did we hit anything?
        if collision(rock_type, cx, cy, pit):
            # yes! our run is over
            cy = old_cy
#             print(f"after checks: ({cx}, {cy})")
            break
            
#         print(f"after checks: ({cx}, {cy})")

    place(rock_type, cx, cy, pit)
    bottom = max(bottom, cy + rock_heights[rock_type] - 1)
    rock_type = (rock_type + 1) % n_types

t1 = time.time()
print(f"simulating {n_rocks} rocks took {t1 - t0:.3g} seconds")
print(f"the tower is {bottom} units tall")
