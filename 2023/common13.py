from typing import Optional, TypeVar, Sequence

from utils import Matrix


T = TypeVar("T")


def find_row_reflection(
    mat: Matrix[T], exclude: Optional[Sequence[int]] = None
) -> Optional[int]:
    """Find the row around which the matrix contains is reflected.

    Returns `None` if there is no reflection. Ignores possible reflections around rows
    contained in `exclude`.

    Specifically, this checks whether row `row0 - i` is identical to row `row0 + i + 1`
    for every `i` (within bounds).
    """
    # first hash the rows
    hashes = [hash(tuple(row)) for row in mat.data]

    # next check for reflection at every position
    if exclude is None:
        exclude = []
    for row0 in range(mat.nrows - 1):
        if row0 in exclude:
            continue

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
