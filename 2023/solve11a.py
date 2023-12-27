#! /usr/bin/env python
from types import SimpleNamespace
from typing import List, Tuple

from utils import loadmatrix, logger, Matrix


def parse_image(img: Matrix) -> SimpleNamespace:
    galaxies = []
    empty_rows = []
    for i, row in enumerate(img.data):
        empty_row = True
        for j, elem in enumerate(row):
            if elem == "#":
                galaxies.append((i, j))
                empty_row = False
            else:
                assert elem == "."

        if empty_row:
            empty_rows.append(i)

    empty_cols = []
    for j in range(img.ncols):
        empty_col = True
        for i in range(img.nrows):
            if img[i, j] != ".":
                empty_col = False

        if empty_col:
            empty_cols.append(j)

    res = SimpleNamespace(
        galaxies=galaxies, empty_rows=empty_rows, empty_cols=empty_cols
    )
    return res


def _expanded_1d(i1: int, i2: int, empty: List[int]) -> int:
    m = min(i1, i2)
    M = max(i1, i2)

    to_expand = [_ for _ in empty if m <= _ <= M]
    return abs(M - m) + len(to_expand)


def expanded_distance(
    a: Tuple[int, int], b: Tuple[int, int], empty_rows: List[int], empty_cols: List[int]
) -> int:
    """This is Manhattan distance, with some columns or rows expanded."""
    d_rows = _expanded_1d(a[0], b[0], empty_rows)
    d_cols = _expanded_1d(a[1], b[1], empty_cols)
    return d_rows + d_cols


if __name__ == "__main__":
    img = loadmatrix()
    logger.debug(f"{img}")

    galaxy_info = parse_image(img)
    logger.debug(
        f"{len(galaxy_info.galaxies)} galaxies, "
        f"{len(galaxy_info.empty_rows)} empty rows, "
        f"{len(galaxy_info.empty_cols)} empty cols"
    )
    logger.debug(f"{galaxy_info}")

    pair_distances = []
    for i, a in enumerate(galaxy_info.galaxies):
        for j, b in enumerate(galaxy_info.galaxies[i + 1 :], i + 1):
            d = expanded_distance(a, b, galaxy_info.empty_rows, galaxy_info.empty_cols)
            pair_distances.append(d)
            logger.debug(f"distance between galaxy {i} and galaxy {j} is {d}")

    s = sum(pair_distances)
    print(f"The sum of the lengths of all paired shortest paths is {s}")
