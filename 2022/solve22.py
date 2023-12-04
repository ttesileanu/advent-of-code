#! /usr/bin/env python
import sys
from typing import List, Tuple


def parse_path(s: str) -> List[Tuple[int, str]]:
    idx = 0
    res = []
    while idx < len(s):
        idx_end = idx
        while idx_end < len(s) and s[idx_end].isdigit():
            idx_end += 1

        assert idx_end > idx
        count = int(s[idx:idx_end])

        idx = idx_end
        if idx < len(s):
            rotation = s[idx]
            idx += 1
        else:
            rotation = "."

        res.append((count, rotation))

    return res


def get_starting_cfg(board: List[List[str]]) -> Tuple[int, int, str]:
    assert all(_ == " " for _ in board[0])

    row = 1
    col = board[1].index(".")
    facing = ">"

    return row, col, facing


def step(position: List, board: List[List[str]]):
    row, col, facing = position

    step_map = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}
    step = step_map[facing]

    row += step[0]
    col += step[1]
    if board[row][col] == " ":
        # need to wrap around
        while board[row - step[0]][col - step[1]] != " ":
            row -= step[0]
            col -= step[1]

    position[0] = row
    position[1] = col


def simulate(
    board: List[List[str]], path: List[Tuple[int, str]], start: Tuple[int, int, str]
) -> Tuple[int, int, str]:
    position = list(start)

    rotation_map = {
        "L": {">": "^", "v": ">", "<": "v", "^": "<"},
        "R": {">": "v", "v": "<", "<": "^", "^": ">"},
        ".": {">": ">", "v": "v", "<": "<", "^": "^"},
    }

    trajectory = [list(row) for row in board]

    for count, rotation in path:
        for k in range(count):
            trajectory[position[0]][position[1]] = position[2]
            old_position = list(position)
            step(position, board)

            assert board[position[0]][position[1]] in "#."
            if board[position[0]][position[1]] == "#":
                # ran into a wall!
                position = old_position
                break

        position[-1] = rotation_map[rotation][position[-1]]

    for row in trajectory:
        print("".join(row))

    return position


fname = "input22" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    # add some padding to the board
    board = [[]]
    width = 0
    for line in f:
        line = line.rstrip()
        if len(line) == 0:
            # map ended
            break

        line_lst = [" "] + list(line) + [" "]
        board.append(line_lst)
        width = max(width, len(line_lst))

    board.append([])

    for row in board:
        row.extend((width - len(row)) * [" "])

    while len(line) == 0:
        line = next(f).strip()

    path_str = line

assert all(len(row) == width for row in board)

path = parse_path(path_str)

# for row in board:
#     print("".join(row))

# print(path)
print(f"path length upper bound: {sum(_[0] for _ in path)}")

start = get_starting_cfg(board)
final = simulate(board, path, start)

print(f"ended at row: {final[0]}, col: {final[1]}, facing: {final[2]}")

facing_map = {">": 0, "v": 1, "<": 2, "^": 3}
password = 1000 * final[0] + 4 * final[1] + facing_map[final[2]]
print(f"password: {password}")
