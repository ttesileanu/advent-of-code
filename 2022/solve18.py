#! /usr/bin/env python
import sys

fname = "input18" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    cubes = set()
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        coords = tuple(int(_) for _ in line.split(","))
        assert len(coords) == 3

        cubes.add(coords)

surface = 0
for x, y, z in cubes:
    if (x + 1, y, z) not in cubes:
        surface += 1
    if (x - 1, y, z) not in cubes:
        surface += 1
    if (x, y + 1, z) not in cubes:
        surface += 1
    if (x, y - 1, z) not in cubes:
        surface += 1
    if (x, y, z + 1) not in cubes:
        surface += 1
    if (x, y, z - 1) not in cubes:
        surface += 1

print(f"surface area: {surface}")
