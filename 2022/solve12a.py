#! /usr/bin/env python
from typing import List, Tuple
from collections import deque

def convert(s: str) -> str:
    if s == "S":
        s = "a"
    if s == "E":
        s = "z"
        
    return s


def valid(start: str, end: str) -> bool:
    start = convert(start)
    end = convert(end)

    return ord(start) <= ord(end) + 1


def dfs(
    i: int,
    j: int,
    elevation: List[str],
    target: str = "a",
    depth: int = 0,
) -> Tuple[int, List[List[str]], int, int]:
    m = len(elevation)
    n = len(elevation[0])

    q = deque([(i, j, depth)])

    visited = [n * [False] for _ in elevation]
    pred = [n * ["."] for _ in elevation]
    while len(q) > 0:
        ci, cj, cdepth = q.popleft()
        if visited[ci][cj]:
            # already visited
            continue
            
        visited[ci][cj] = True

        height = elevation[ci][cj]
        if height == target:
            return cdepth, pred, ci, cj

        if (
            ci + 1 < m
            and not visited [ci + 1][cj]
            and valid(height, elevation[ci + 1][cj])
        ):
            pred[ci + 1][cj] = "^"
            q.append((ci + 1, cj, cdepth + 1))
            
        if (
            ci - 1 >= 0
            and not visited [ci - 1][cj]
            and valid(height, elevation[ci - 1][cj])
        ):
            pred[ci - 1][cj] = "v"
            q.append((ci - 1, cj, cdepth + 1))

        if (
            cj + 1 < n
            and not visited [ci][cj + 1]
            and valid(height, elevation[ci][cj + 1])
        ):
            pred[ci][cj + 1] = "<"
            q.append((ci, cj + 1, cdepth + 1))
            
        if (
            cj - 1 >= 0
            and not visited [ci][cj - 1]
            and valid(height, elevation[ci][cj - 1])
        ):
            pred[ci][cj - 1] = ">"
            q.append((ci, cj - 1, cdepth + 1))

    raise RuntimeError("target not found")


with open("input12.txt", "rt") as f:
    elevation = []
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        elevation.append(line)

Ei, Ej = None, None
for i, row in enumerate(elevation):
    if "E" in row:
        Ei = i
        Ej = row.index("E")

print(f"ending at ({Ei}, {Ej})")

n_steps, pred, fi, fj = dfs(Ei, Ej, elevation)

n = len(elevation[0])
directions = [n * ["."] for _ in elevation]
directions[fi][fj] = "a"
ci, cj = fi, fj
while elevation[ci][cj] != "E":
    rev_dir = pred[ci][cj]
    if rev_dir == "^":
        ci -= 1
        directions[ci][cj] = "^"
    elif rev_dir == "v":
        ci += 1
        directions[ci][cj] = "v"
    elif rev_dir == "<":
        cj -= 1
        directions[ci][cj] = "<"
    elif rev_dir == ">":
        cj += 1
        directions[ci][cj] = ">"
    else:
        raise ValueError(f"found rev_dir = {rev_dir}")

directions[Ei][Ej] = "E"

for row in directions:
    print(row)

print(f"shortest path has {n_steps} steps")
