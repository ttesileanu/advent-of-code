#! /usr/bin/env python
from bisect import bisect_left

from utils import loadmatrix, logger, Matrix

CUBE = "#"
ROUND = "O"
EMPTY = "."


def tilt_north(mat: Matrix[str]):
    # keeps track of occupied spots for every column
    # this can either be a # or the latest O that fell on one of the #
    # there can be multiple barriers for each column, sorted in increasing order
    barriers = []
    for col in range(mat.ncols):
        # row -1 functions as a barrier
        col_barriers = [-1]
        for row in range(mat.nrows):
            if mat[row, col] == CUBE:
                col_barriers.append(row)

        barriers.append(col_barriers)
        logger.debug(f"Column {col} has initial barriers at {col_barriers}")

    for row in range(mat.nrows):
        for col in range(mat.ncols):
            if mat[row, col] == ROUND:
                col_barriers = barriers[col]

                # find the closest barrier above this round stone
                idx = bisect_left(col_barriers, row)
                assert idx > 0

                barrier = col_barriers[idx - 1]
                assert barrier < row

                fall_row = barrier + 1
                if fall_row != row:
                    mat[fall_row, col] = ROUND
                    mat[row, col] = EMPTY
                    logger.debug(f"Rock from {(row, col)} fell to {(fall_row, col)}")
                else:
                    logger.debug(f"Rock from {(row, col)} stayed there")

                barriers[col][idx - 1] += 1
                if idx < len(col_barriers):
                    assert col_barriers[idx - 1] < col_barriers[idx]


def get_total_north_load(mat: Matrix[str]) -> int:
    load = 0
    for i, row in enumerate(mat.data):
        n_round = row.count("O")
        row_multiplier = mat.nrows - i
        load += n_round * row_multiplier

    return load


if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"Matrix before tilting: {mat!s}")
    tilt_north(mat)
    logger.debug(f"Matrix after tilting: {mat!s}")

    total_north_load = get_total_north_load(mat)
    print(f"Total load on north support beams is {total_north_load}")
