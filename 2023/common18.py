from typing import Literal, Sequence, Tuple

from utils import logger


Direction = Literal["R", "D", "L", "U"]


# 1 = ccw, -1 = cw
ROTATION_MAP = {
    ("R", "U"): 1,
    ("R", "D"): -1,
    ("L", "U"): -1,
    ("L", "D"): 1,
    ("U", "R"): -1,
    ("U", "L"): 1,
    ("D", "R"): 1,
    ("D", "L"): -1,
}


def overall_rotation(directions: Sequence[Direction]) -> int:
    rot = 0
    for dir1, dir2 in zip(directions[:-1], directions[1:]):
        rot += ROTATION_MAP[dir1, dir2]
    rot += ROTATION_MAP[directions[-1], directions[0]]

    return rot


def outline_to_path(
    outline: Sequence[Tuple[Direction, int]]
) -> Sequence[Tuple[int, int]]:
    assert len(outline) > 1

    path = []

    overall_rot = overall_rotation([_[0] for _ in outline])
    assert abs(overall_rot) == 4

    overall_rot = 1 if overall_rot > 0 else -1
    orientation = "ccw" if overall_rot > 0 else "cw"
    logger.debug(f"{orientation=} {overall_rot=}.")

    i, j = 0, 0
    for k, (dir, count) in enumerate(outline):
        prev_dir = outline[(k - 1) % len(outline)][0]
        turn_rot = ROTATION_MAP[prev_dir, dir]

        corner = prev_dir + dir
        if corner == "UR" or corner == "LD":
            di, dj = (0, 0) if turn_rot == overall_rot else (1, 1)
        elif corner == "UL" or corner == "RD":
            di, dj = (0, 1) if turn_rot == overall_rot else (1, 0)
        elif corner == "DL" or corner == "RU":
            di, dj = (1, 1) if turn_rot == overall_rot else (0, 0)
        elif corner == "LU" or corner == "DR":
            di, dj = (1, 0) if turn_rot == overall_rot else (0, 1)
        else:
            raise ValueError(f"Unknown {corner=}")

        path.append((i + di, j + dj))
        if dir == "L":
            j -= count
        elif dir == "R":
            j += count
        elif dir == "U":
            i -= count
        elif dir == "D":
            i += count

    path.append(path[0])
    for (i1, j1), (i2, j2) in zip(path[:-1], path[1:]):
        assert i1 == i2 or j1 == j2, f"({i1}, {j1}) -- ({i2}, {j2})"

    return path


def area_inside(outline: Sequence[Tuple[Direction, int]]) -> int:
    path = outline_to_path(outline)
    area = 0
    for (i1, j1), (i2, j2) in zip(path[:-1], path[1:]):
        dj = j2 - j1
        if dj != 0:
            assert i1 == i2
            area += i1 * dj

    return abs(area)
