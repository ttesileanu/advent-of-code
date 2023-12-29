#! /usr/bin/env python
from typing import Optional, Tuple, TypeVar

from utils import itermatrix, Matrix, logger

from common13 import find_row_reflection

T = TypeVar("T")


def find_smudged_reflection(
    mat: Matrix[T], exclude: Optional[int]
) -> Tuple[Optional[int], Optional[Tuple[int, int]]]:
    exclude = [] if exclude is None else [exclude]

    # naive approach: check for smudges everywhere
    FLIP = {".": "#", "#": "."}
    for row in range(mat.nrows):
        for col in range(mat.ncols):
            mat[row, col] = FLIP[mat[row, col]]

            refl_row = find_row_reflection(mat, exclude=exclude)

            # set it back to what it was
            mat[row, col] = FLIP[mat[row, col]]

            if refl_row is not None:
                return refl_row, (row, col)

    return None, None


if __name__ == "__main__":
    refl_rows = []
    refl_cols = []
    for mat in itermatrix():
        row0 = find_row_reflection(mat)
        row1, smudge_rows = find_smudged_reflection(mat, exclude=row0)

        mat_t = mat.transpose()
        col0 = find_row_reflection(mat_t)
        col1, smudge_cols_t = find_smudged_reflection(mat_t, exclude=col0)
        smudge_cols = smudge_cols_t[::-1] if smudge_cols_t is not None else None

        logger.debug(f"{row0=}, {col0=}, {row1=}, {col1=}")
        logger.debug(f"{smudge_rows=}, {smudge_cols=}")

        assert row1 is not None or col1 is not None
        assert row1 is None or col1 is None

        if row1 is not None:
            refl_rows.append(row1 + 1)
        elif col1 is not None:
            refl_cols.append(col1 + 1)

    summary = sum(100 * _ for _ in refl_rows) + sum(refl_cols)
    print(f"Summary of reflection notes is {summary}")
