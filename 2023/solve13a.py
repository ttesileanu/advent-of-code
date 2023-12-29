#! /usr/bin/env python
from typing import Optional, TypeVar

from utils import itermatrix, Matrix


T = TypeVar("T")


def find_row_reflection(mat: Matrix[T]) -> Optional[int]:
    """Find the row around which the matrix contains is reflected.

    Returns `None` if there is no reflection.

    Specifically, this checks whether row `row0 - i` is identical to row `row0 + i + 1`
    for every `i` (within bounds).
    """
    # first hash the rows
    hashes = [hash(tuple(row)) for row in mat.data]

    # next check for reflection at every position
    for row0 in range(mat.nrows - 1):
        # count how many rows should match
        n = min(row0 + 1, mat.nrows - row0 - 1)
        is_match = True
        for k in range(n):
            if hashes[row0 - k] != hashes[row0 + k + 1]:
                is_match = False
                break

        if is_match:
            # double check that this wasn't a hashing fluke
            for k in range(n):
                if mat.data[row0 - k] != mat.data[row0 + k + 1]:
                    is_match = False
                    break

            if is_match:
                return row0

    return None


if __name__ == "__main__":
    refl_rows = []
    refl_cols = []
    for mat in itermatrix():
        row0 = find_row_reflection(mat)
        if row0 is None:
            col0 = find_row_reflection(mat.transpose())
            assert col0 is not None

            refl_cols.append(col0 + 1)
        else:
            refl_rows.append(row0 + 1)

    summary = sum(100 * _ for _ in refl_rows) + sum(refl_cols)
    print(f"Summary of reflection notes is {summary}")
