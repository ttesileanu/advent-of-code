#! /usr/bin/env python
from utils import loadmatrix, logger

from common14 import tilt_north, get_total_north_load


if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"Matrix before tilting: {mat!s}")
    tilt_north(mat)
    logger.debug(f"Matrix after tilting: {mat!s}")

    total_north_load = get_total_north_load(mat)
    print(f"Total load on north support beams is {total_north_load}")
