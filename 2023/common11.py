from types import SimpleNamespace
from typing import List, Tuple

from utils import Matrix


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


def _expanded_1d(i1: int, i2: int, empty: List[int], factor: int = 2) -> int:
    m = min(i1, i2)
    M = max(i1, i2)

    to_expand = [_ for _ in empty if m <= _ <= M]
    return abs(M - m) + len(to_expand) * (factor - 1)


def expanded_distance(
    a: Tuple[int, int],
    b: Tuple[int, int],
    empty_rows: List[int],
    empty_cols: List[int],
    factor: int = 2,
) -> int:
    """This is Manhattan distance, with some columns or rows expanded."""
    d_rows = _expanded_1d(a[0], b[0], empty_rows, factor=factor)
    d_cols = _expanded_1d(a[1], b[1], empty_cols, factor=factor)
    return d_rows + d_cols
