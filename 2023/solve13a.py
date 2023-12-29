#! /usr/bin/env python
from utils import itermatrix

from common13 import find_row_reflection

if __name__ == "__main__":
    refl_rows = []
    refl_cols = []
    for mat in itermatrix():
        row0 = find_row_reflection(mat)
        col0 = find_row_reflection(mat.transpose())
        assert row0 is not None or col0 is not None

        assert row0 is None or col0 is None
        if row0 is not None:
            refl_rows.append(row0 + 1)
        elif col0 is not None:
            refl_cols.append(col0 + 1)

    summary = sum(100 * _ for _ in refl_rows) + sum(refl_cols)
    print(f"Summary of reflection notes is {summary}")
