#! /usr/bin/env python
import sys
from dataclasses import dataclass
from typing import List, Union, Tuple
from copy import deepcopy
from collections import deque


direction_map = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}


@dataclass
class Storm:
    row: int = 0
    col: int = 0
    direction: Tuple[int] = (0, 0)
    direction_str: str = ""

    def __init__(self, row: int, col: int, direction: str):
        self.row = row
        self.col = col
        self.direction_str = direction
        self.direction = direction_map[direction]


class StormSystem:
    def __init__(self, board: List[str]):
        self.min_row = 1
        self.min_col = 1    
    
        self.n_rows = len(board) - 2
        self.n_cols = len(board[0]) - 2
        self.initial, self.walls = self._parse(board)

        self.start = (0, board[0].index("."))
        self.finish = (len(board) - 1, board[-1].index("."))

        self.board_cache = {0: self.initial}

    def predict(self, n: int) -> List[List[str]]:
        """Predict the board after `n` steps.

        If multiple storms are at the same position, an "x" is placed on the map.
        """
        if n not in self.board_cache:
            future = deepcopy(self.walls)
            for storm in self.initial:
                row, col = self._predict_storm(storm, n)

                if future[row][col] == ".":
                    future[row][col] = storm.direction_str
                else:
                    future[row][col] = "x"

            self.board_cache[n] = future

        return self.board_cache[n]

    def _parse(self, board: List[str]) -> Tuple[List[Storm], List[List[str]]]:
        storms = []
        walls = []
        for i, row in enumerate(board):
            wall_row = []
            for j, ch in enumerate(row):
                if ch in "<>^v":
                    storms.append(Storm(i, j, ch))
                
                wall_row.append("#" if ch == "#" else ".")

            walls.append(wall_row)

        return storms, walls
        
    def _predict_storm(self, storm: Storm, n: int) -> Tuple[int, int]:
        """Predict position of `storm` after `n` steps."""
        dx = n * storm.direction[0]
        dy = n * storm.direction[1]
        row = self.min_row + (storm.row + dx - self.min_row) % self.n_rows
        col = self.min_col + (storm.col + dy - self.min_col) % self.n_cols
        return row, col


def bfs(
    system: StormSystem, t0: int = 0, reverse: bool = False
) -> Tuple[int, List[Tuple[int, int]]]:
    if not reverse:
        start = system.start
        finish = system.finish
    else:
        start = system.finish
        finish = system.start
    
    node = start + (0,)
    q = deque([node])
    parents = {node: None}
    explored = set([node])

    found = False
    while len(q) > 0:
        node = q.popleft()
        row, col, depth = node

        if (row, col) == finish:
            found = True
            break

        storms = system.predict(t0 + depth + 1)

        trial = (row - 1, col, depth + 1)
        if row > 0 and storms[row - 1][col] == "." and trial not in explored:
            q.append(trial)
            explored.add(trial)
            parents[trial] = node
            
        trial = (row + 1, col, depth + 1)
        if row + 1 < len(storms):
            if storms[row + 1][col] == "." and trial not in explored:
                q.append(trial)
                explored.add(trial)
                parents[trial] = node
            
        trial = (row - 1, col, depth + 1)
        if storms[row - 1][col] == "." and trial not in explored:
            q.append(trial)
            explored.add(trial)
            parents[trial] = node
            
        trial = (row, col - 1, depth + 1)
        if storms[row][col - 1] == "." and trial not in explored:
            q.append(trial)
            explored.add(trial)
            parents[trial] = node
            
        trial = (row, col + 1, depth + 1)
        if storms[row][col + 1] == "." and trial not in explored:
            q.append(trial)
            explored.add(trial)
            parents[trial] = node
            
        trial = (row, col, depth + 1)
        if storms[row][col] == "." and trial not in explored:
            q.append(trial)
            explored.add(trial)
            parents[trial] = node

    assert found

    trajectory = []
    while node is not None:
        trajectory.append(node[:2])
        node = parents[node]

    trajectory = trajectory[::-1]

    assert depth + 1 == len(trajectory)
    
    return depth, trajectory


fname = "input24" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    board = []
    width = None
    for line in f:
        line = line.strip()
        if len(line) == 0:
            # map ended
            break

        assert line[0] == "#"
        assert line[-1] == "#"

        board.append(line)
        if width == None:
            width = len(line)
        else:
            assert len(line) == width

n_available = 0
for row in board:
    print("".join(row))
    n_available += sum(_ == "." for _ in row)

print(f"number of available squares: {n_available}")

system = StormSystem(board)

n_fwd, _ = bfs(system)
print(f"going from {system.start} to {system.finish} in {n_fwd} steps")

n_back, _ = bfs(system, t0=n_fwd, reverse=True)
print(f"going from back to {system.start} in {n_back} steps")

n_fwd_again, _ = bfs(system, t0=n_fwd + n_back)
print(f"going from {system.start} to {system.finish} again in {n_fwd_again} steps")

print(f"total minimal duration: {n_fwd + n_back + n_fwd_again}")
