#! /usr/bin/env python
import sys
import numpy as np


def dfs(steam: np.ndarray, x: int, y: int, z: int):
    m, n, p = steam.shape

    stack = [(x, y, z)]
    while len(stack) > 0:
        x, y, z = stack.pop()
        steam[x, y, z] = 1

        if x + 1 < m and steam[x + 1, y, z] == 0:
            stack.append((x + 1, y, z))
        if y + 1 < n and steam[x, y + 1, z] == 0:
            stack.append((x, y + 1, z))
        if z + 1 < p and steam[x, y, z + 1] == 0:
            stack.append((x, y, z + 1))
            
        if x > 0 and steam[x - 1, y, z] == 0:
            stack.append((x - 1, y, z))
        if y > 0 and steam[x, y - 1, z] == 0:
            stack.append((x, y - 1, z))
        if z > 0 and steam[x, y, z - 1] == 0:
            stack.append((x, y, z - 1))


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

min_x = min_y = min_z = np.inf
max_x = max_y = max_z = -np.inf
for x, y, z in cubes:
    min_x = min(min_x, x)
    min_y = min(min_y, y)
    min_z = min(min_z, z)
    
    max_x = max(max_x, x)
    max_y = max(max_y, y)
    max_z = max(max_z, z)

# add a boundary around the droplet
min_x -= 1
min_y -= 1
min_z -= 1

max_x += 1
max_y += 1
max_z += 1

# make a volumetric representation
n_x = max_x - min_x + 1
n_y = max_y - min_y + 1
n_z = max_z - min_z + 1

steam = np.zeros((n_x, n_y, n_z), dtype=int)

# add the cubes
for x, y, z in cubes:
    steam[x - min_x][y - min_y][z - min_z] = -1

# fill everything that's reachable from the outside with gas
dfs(steam, 0, 0, 0)

surface = 0
for x, y, z in cubes:
    x -= min_x
    y -= min_y
    z -= min_z

    if steam[x + 1, y, z] == 1:
        surface += 1
    if steam[x - 1, y, z] == 1:
        surface += 1
    if steam[x, y + 1, z] == 1:
        surface += 1
    if steam[x, y - 1, z] == 1:
        surface += 1
    if steam[x, y, z + 1] == 1:
        surface += 1
    if steam[x, y, z - 1] == 1:
        surface += 1

print(f"exterior surface area: {surface}")
