#! /usr/bin/env python
import sys
from typing import List, Tuple, Dict, Union


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


def on_stitch(
    row: int, col: int, stitch: Dict[str, Union[str, Tuple[int, int]]], which: str
) -> bool:
    start = stitch.get("from_" + which)
    end = stitch.get("to_" + which)

    min_row = min(start[0], end[0])
    max_row = max(start[0], end[0])
    min_col = min(start[1], end[1])
    max_col = max(start[1], end[1])

    return (min_row <= row <= max_row) and (min_col <= col <= max_col)


def step(
    position: List,
    board: List[List[str]],
    stitches: Dict[str, Dict[str, Union[str, Tuple[int, int]]]],
):
    row, col, facing = position

    step_map = {">": (0, 1), "<": (0, -1), "^": (-1, 0), "v": (1, 0)}
    step = step_map[facing]

    reverse_map = {">": "<", "<": ">", "^": "v", "v": "^"}

    row += step[0]
    col += step[1]
    if board[row][col] == " ":
        # need to move to a different face
        # first go back to the previous position...
        row -= step[0]
        col -= step[1]

        # ...next figure out which stitch we're on
        turn = None
        for stitch in stitches.values():
            if on_stitch(row, col, stitch, "a") and facing == stitch["turn"][0]:
                from_a = stitch["from_a"]
                to_a = stitch["to_a"]
                from_b = stitch["from_b"]
                to_b = stitch["to_b"]
                turn = stitch["turn"]

                break
            elif (
                on_stitch(row, col, stitch, "b")
                and facing == reverse_map[stitch["turn"][1]]
            ):
                from_a = stitch["from_b"]
                to_a = stitch["to_b"]
                from_b = stitch["from_a"]
                to_b = stitch["to_a"]
                turn = [reverse_map[_] for _ in stitch["turn"][::-1]]

                break

        assert turn[0] == facing, f"{row}, {col}; {stitch}; {turn}, {facing}"
        assert turn is not None

        delta_a = [to_a[_] - from_a[_] for _ in range(2)]
        delta_b = [to_b[_] - from_b[_] for _ in range(2)]

        print(f"wrap from ({row}, {col}, {facing}) ", end="")

        if delta_a[0] == 0:
            row = from_b[0] + delta_b[0] * (col - from_a[1]) // delta_a[1]
            col = from_b[1] + delta_b[1] * (col - from_a[1]) // delta_a[1]
        else:
            assert delta_a[0] != 0
            col = from_b[1] + delta_b[1] * (row - from_a[0]) // delta_a[0]
            row = from_b[0] + delta_b[0] * (row - from_a[0]) // delta_a[0]

        facing = turn[1]

        print(f"to ({row}, {col}, {facing})")

    position[0] = row
    position[1] = col
    position[2] = facing


def simulate(
    board: List[List[str]],
    path: List[Tuple[int, str]],
    start: Tuple[int, int, str],
    stitches: Dict[str, Dict[str, Union[str, Tuple[int, int]]]],
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
            step(position, board, stitches)

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
    cube_edge = None
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

# check the cube structure
# ugh: the small and big examples have different structures...
if width < 100:
    assert (width - 2) % 4 == 0
    cube_edge = (width - 2) // 4
    assert len(board) == cube_edge * 3 + 2
    # e.g., 4: front, 1: top, 3: left, 2: back, 5: bottom, 6: right
    faces = ["  1 ", "234 ", "  56"]
    stitches = {
        "13": {
            "from_a": (1, 9),
            "to_a": (4, 9),
            "from_b": (5, 5),
            "to_b": (5, 8),
            "turn": "<v",
        },
        "16": {
            "from_a": (1, 12),
            "to_a": (4, 12),
            "from_b": (12, 16),
            "to_b": (9, 16),
            "turn": "><",
        },
        "12": {
            "from_a": (1, 9),
            "to_a": (1, 12),
            "from_b": (5, 4),
            "to_b": (5, 1),
            "turn": "^v",
        },
        "26": {
            "from_a": (5, 1),
            "to_a": (8, 1),
            "from_b": (12, 16),
            "to_b": (12, 13),
            "turn": "<^",
        },
        "46": {
            "from_a": (5, 12),
            "to_a": (8, 12),
            "from_b": (9, 16),
            "to_b": (9, 13),
            "turn": ">v",
        },
        "53": {
            "from_a": (9, 9),
            "to_a": (9, 12),
            "from_b": (8, 8),
            "to_b": (8, 5),
            "turn": "<^",
        },
        "25": {
            "from_a": (8, 1),
            "to_a": (8, 4),
            "from_b": (12, 12),
            "to_b": (12, 9),
            "turn": "v^",
        },
    }
else:
    assert (width - 2) % 3 == 0
    cube_edge = (width - 2) // 3
    assert len(board) == cube_edge * 4 + 2
    # e.g., 4: front, 1: top, 3: left, 2: back, 5: bottom, 6: right
    faces = [" 16", " 4 ", "35 ", "2  "]
    # neighbors done: 1, 6, 4, 3, 5, 2
    stitches = {
        "13": {                 # CHECK
            "from_a": (1, 51),
            "to_a": (50, 51),
            "from_b": (150, 1),
            "to_b": (101, 1),
            "turn": "<>",
        },
        "65": {                 # CHECK
            "from_a": (1, 150),
            "to_a": (50, 150),
            "from_b": (150, 100),
            "to_b": (101, 100),
            "turn": "><",
        },
        "12": {                 # CHECK
            "from_a": (1, 51),
            "to_a": (1, 100),
            "from_b": (151, 1),
            "to_b": (200, 1),
            "turn": "^>",
        },
        "62": {                 # CHECK
            "from_a": (1, 101),
            "to_a": (1, 150),
            "from_b": (200, 1),
            "to_b": (200, 50),
            "turn": "^^",
        },
        "64": {                 # CHECK
            "from_a": (50, 101),
            "to_a": (50, 150),
            "from_b": (51, 100),
            "to_b": (100, 100),
            "turn": "v<",
        },
        "43": {                 # CHECK
            "from_a": (51, 51),
            "to_a": (100, 51),
            "from_b": (101, 1),
            "to_b": (101, 50),
            "turn": "<v",
        },
        "52": {                 # CHECK
            "from_a": (150, 51),
            "to_a": (150, 100),
            "from_b": (151, 50),
            "to_b": (200, 50),
            "turn": "v<",
        },
    }

for i in range(len(board)):
    for j in range(width):
        ch = board[i][j]
        if i == 0 or j == 0 or i == len(board) - 1 or j == width - 1:
            assert ch == " "
        else:
            face_i = (i - 1) // cube_edge
            face_j = (j - 1) // cube_edge
            face_ch = faces[face_i][face_j]

            if face_ch == " ":
                assert ch == " "
            else:
                assert ch in "#."

path = parse_path(path_str)

# for row in board:
#     print("".join(row))

# print(path)
print(f"path length upper bound: {sum(_[0] for _ in path)}")

start = get_starting_cfg(board)
final = simulate(board, path, start, stitches)

print(f"ended at row: {final[0]}, col: {final[1]}, facing: {final[2]}")

facing_map = {">": 0, "v": 1, "<": 2, "^": 3}
password = 1000 * final[0] + 4 * final[1] + facing_map[final[2]]
print(f"password: {password}")
