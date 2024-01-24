#! /usr/bin/env python
from typing import Set, Tuple

from utils import loadmatrix, logger, Matrix


START = "S"
GARDEN = "."
ROCK = "#"

# N_STEPS = 6
N_STEPS = 64


def forward(mat: Matrix[str], locations: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    res = set()
    for loc in locations:
        for neigh in mat.iterneighbors(*loc, diagonals=False):
            if mat[neigh] == GARDEN:
                res.add(neigh)

    return res


if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"{mat=}")

    start = None
    for i, row in enumerate(mat.data):
        if row.count(START) > 0:
            assert start is None
            assert row.count(START) == 1
            start = (i, row.index(START))

    logger.info(f"Starting from {start}")
    mat[start[0], start[1]] = GARDEN

    locations = {start}
    for i in range(N_STEPS):
        locations = forward(mat, locations)

    print(f"The elf can reach {len(locations)} plots in {N_STEPS} steps")
