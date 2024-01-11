#! /usr/bin/env python
import re
from utils import iterinput, logger, Matrix
from collections import deque

try:
    import matplotlib.pyplot as plt
    import numpy as np

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False


DIRECTION_MAP = {"R": (0, 1), "L": (0, -1), "U": (-1, 0), "D": (1, 0)}
DUG = "#"
GROUND = "."


def fill(mat: Matrix[str], i: int, j: int, dug: str = DUG):
    q = deque()
    q.append((i, j))

    while q:
        ci, cj = q.popleft()
        mat[ci, cj] = dug
        for ni, nj in mat.iterneighbors(ci, cj, diagonals=False):
            if mat[ni, nj] != dug:
                q.append((ni, nj))

        count += 1


def span_fill(mat: Matrix[str], i: int, j: int, dug: str = DUG):
    q = deque()
    q.append((i, i, j, 1))
    q.append((i, i, j - 1, -1))
    while q:
        i1, i2, j, dj = q.popleft()

        i = i1
        while mat[i - 1, j] != dug:
            mat[i - 1, j] = dug
            i -= 1
        if i < i1:
            q.append((i, i1 - 1, j - dj, -dj))

        while i1 <= i2:
            while mat[i1, j] != dug:
                mat[i1, j] = dug
                i1 += 1

            if i1 > i:
                q.append((i, i1 - 1, j + dj, dj))
            if i1 - 1 > i2:
                q.append((i2 + 1, i1 - 1, j - dj, -dj))
            i1 += 1
            while i1 < i2 and mat[i1, j] == dug:
                i1 += 1
            i = i1


if FANCY_PLOTTING:

    def show_matrix(mat: Matrix, dug: str = DUG) -> plt.Axes:
        _, ax = plt.subplots()

        mat_num = np.asarray(mat.data) == dug
        ax.imshow(mat_num)

        plt.show()
        return ax


if __name__ == "__main__":
    regex = re.compile(r"([RDLU])\s+(\d+)\s+\(#([0-9a-fA-F]+)\)")
    dig_plan = []
    for line in iterinput():
        match = regex.fullmatch(line)
        assert match is not None

        dir, count_str, color = match.groups()
        count = int(count_str)

        dig_plan.append((dir, count, color))

    outline = []
    i, j = 0, 0
    min_i, min_j, max_i, max_j = 0, 0, 0, 0
    for dir, count, _ in dig_plan:
        di, dj = DIRECTION_MAP[dir]
        for _ in range(count):
            i += di
            j += dj
            outline.append((i, j))

            min_i = min(min_i, i)
            max_i = max(max_i, i)
            min_j = min(min_j, j)
            max_j = max(max_j, j)

    logger.debug(f"i range = [{min_i}, {max_i}], j range = [{min_j}, {max_j}]")
    logger.debug(f"{outline=}")

    nrows = max_i - min_i + 1
    ncols = max_j - min_j + 1
    mat = Matrix([ncols * [GROUND] for _ in range(nrows)])
    for i, j in outline:
        mat[i - min_i, j - min_j] = "#"

    logger.debug(f"Map before filling: {mat}")

    # find a point that's inside our contour so we know what to fill
    fill_start = None
    assert nrows >= 2
    assert ncols >= 2
    for j in range(ncols):
        if mat[0, j] == DUG:
            if mat[1, j] != DUG:
                fill_start = (1, j)
                break
        if mat[nrows - 1, j] == DUG:
            if mat[nrows - 2, j] != DUG:
                fill_start = (nrows - 2, j)
                break

    if fill_start is None:
        for i in range(nrows):
            if mat[i, 0] == DUG:
                if mat[i, 1] != DUG:
                    fill_start = (i, 1)
                    break
            if mat[i, ncols - 1] == DUG:
                if mat[i, ncols - 2] != DUG:
                    fill_start = (i, ncols - 2)
                    break

    assert fill_start is not None
    logger.debug(f"{fill_start=}")

    # fill(mat, *fill_start)
    span_fill(mat, *fill_start)
    logger.debug(f"Map after filling: {mat}")

    count = sum(sum(_ == DUG for _ in row) for row in mat.data)
    print(f"The lagoon would hold {count} cubic meters of lava")

    if FANCY_PLOTTING:
        show_matrix(mat)
