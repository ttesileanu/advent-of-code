#! /usr/bin/env python
from utils import loadmatrix, logger
from common17 import MatrixGraph, FANCY_PLOTTING


if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"Map: {mat}")

    mg = MatrixGraph(mat, min_jump=4, max_jump=10)
    dist, path = mg.shortest((0, 0), (mg.nrows - 1, mg.ncols - 1))

    logger.debug(f"Path: {path}")
    print(f"Shortest path has cost {dist}")

    if FANCY_PLOTTING:
        mg.show_mpl(path=path)
