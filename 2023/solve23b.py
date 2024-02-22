#! /usr/bin/env python
from utils import loadmatrix, logger

from common23 import IntersectionGraph, show_matrix

if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"{mat=}")

    # Without the slopes we can't use the DAG trick. We can still focus on the graph
    # generated by the intersection points and try to iterate over all possible paths
    # from start to end, keeping track of the longest.

    g = IntersectionGraph(mat, slopes=False)

    length, path = g.longest(0, len(g.nodes) - 1)
    logger.debug(f"Longest path: {path}")
    print(f"Longest hike has {length} steps.")
    show_matrix(mat, path=path)