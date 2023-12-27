#! /usr/bin/env python
from typing import Dict, Tuple

from utils import loadmatrix, Matrix

from common10 import FANCY_PLOTTING, find_loop, show_pretty_map


def mark_enclosed(map: Matrix, depths: Dict[Tuple[int, int], int]) -> Matrix:
    """Generate a map marking tiles as either I(n) or O(ut)."""
    res = Matrix([map.ncols * [" "] for _ in range(map.nrows)], map.nrows, map.ncols)
    for i, row in enumerate(map.data):
        # need to keep track of inside / outside for top half and bottom half of cells
        inside = [False, False]
        for j, elem in enumerate(row):
            # only care about positions on the loop for inside/outside determination
            loop_elem = elem if (i, j) in depths else " "

            # start needs to be converted!
            if loop_elem == "S":
                if (i - 1, j) in depths and (i + 1, j) in depths:
                    loop_elem = "|"
                elif (i, j - 1) in depths and (i, j + 1) in depths:
                    loop_elem = "-"
                elif (i - 1, j) in depths and (i, j + 1) in depths:
                    loop_elem = "L"
                elif (i - 1, j) in depths and (i, j - 1) in depths:
                    loop_elem = "J"
                elif (i + 1, j) in depths and (i, j - 1) in depths:
                    loop_elem = "7"
                elif (i + 1, j) in depths and (i, j + 1) in depths:
                    loop_elem = "F"
                else:
                    raise ValueError("S identity cannot be decided")

            if loop_elem == "|":
                inside = [~inside[0], ~inside[1]]
            elif loop_elem in "LJ":
                inside[0] = ~inside[0]
            elif loop_elem in "7F":
                inside[1] = ~inside[1]

            if loop_elem == " ":
                # don't tag the loop itself
                res[i, j] = ["O", "I"][all(inside)]

    return res


if __name__ == "__main__":
    map = loadmatrix()
    farthest_i, farthest_j, depths = find_loop(map)

    enclosed = mark_enclosed(map, depths)
    n_enclosed = sum(sum(_ == "I" for _ in row) for row in enclosed.data)
    print(f"Number of tiles enclosed by loop {n_enclosed}")

    if FANCY_PLOTTING:
        show_pretty_map(
            map, target=(farthest_i, farthest_j), depths=depths, tags=enclosed
        )
