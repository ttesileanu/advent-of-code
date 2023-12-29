#! /usr/bin/env python
import copy

from utils import loadmatrix, logger, Matrix

from common14 import tilt, get_total_north_load


N_CYCLES = 1000000000


def cycle(mat: Matrix[str]):
    tilt(mat, "N")
    tilt(mat, "W")
    tilt(mat, "S")
    tilt(mat, "E")


if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"Matrix before cycles: {mat!s}")

    history = []
    cycle_hashes = {}
    loop_start = None
    loop_length = None
    for i in range(N_CYCLES):
        history.append(copy.deepcopy(mat))
        h = mat.get_hash()
        if h in cycle_hashes:
            # loop detected!
            loop_start = cycle_hashes[h]
            loop_length = i - loop_start
            break

        cycle_hashes[h] = i
        cycle(mat)

    if loop_start is not None:
        assert loop_length is not None

        # result[loop_start + i + k * loop_length] = result[loop_start + i] for all k >= 0
        # I want loop_start + i + k * loop_length = N_CYCLES
        #       i + k * loop_length = N_CYCLES - loop_start
        # --> k = (N_CYCLES - loop_start) // loop_length
        #     i = (N_CYCLES - loop_start) % loop_length
        left = N_CYCLES - loop_start
        k = left // loop_length
        offset = left % loop_length
        mat = history[loop_start + offset]

    logger.debug(f"Matrix after {N_CYCLES:,} cycles: {mat!s}")

    total_north_load = get_total_north_load(mat)
    print(f"Total load on north support beams is {total_north_load}")
