from bisect import bisect_left
from typing import Literal, Union

from utils import logger, Matrix, View


CUBE = "#"
ROUND = "O"
EMPTY = "."


def tilt_north(mat: Union[Matrix[str], View[str]]):
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


def get_total_north_load(mat: Union[Matrix[str], View[str]]) -> int:
    load = 0
    for i, row in enumerate(mat.data):
        n_round = row.count("O")
        row_multiplier = mat.nrows - i
        load += n_round * row_multiplier

    return load


def tilt(mat: Matrix[str], dir: Literal["N", "E", "S", "W"]):
    rot = {"N": 0, "E": -1, "S": -2, "W": -3}[dir]
    view = mat.rotated_view(rot)
    tilt_north(view)


def get_total_load(mat: Matrix[str], dir: Literal["N", "E", "S", "W"]) -> int:
    rot = {"N": 0, "E": -1, "S": -2, "W": -3}[dir]
    view = mat.rotated_view(rot)
    return get_total_north_load(view)
