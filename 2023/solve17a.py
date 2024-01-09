#! /usr/bin/env python
from utils import loadmatrix, logger
from common17 import MatrixGraph, FANCY_PLOTTING


if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"Map: {mat}")

    # We can think of this as finding shortest paths in a bipartite graph. Each part of
    # the graph has nodes corresponding to each position on the map. Edges from graph H
    # run only horizontally, while edges from graph V run only vertically. Each goes
    # one, two, or three squares away, and no more. Since this is a bipartite graph,
    # edges run from H to V or from V to H, but never from a part to itself. The cost of
    # an edge is the sum of the squares traveled along the edge, *including* the last
    # and *excluding* the first.

    # Two extra nodes that connect the two bipartite graphs are needed. One connects to
    # the top-left corner of both H and V with edges of zero cost; this can be used as
    # starting point. A second extra node connect to the bottom-right corner of both H
    # and V with zero cost; this can be used as end point. Our task reduces to finding
    # the lowest-cost path from the first extra node to the second.

    mg = MatrixGraph(mat)
    dist, path = mg.shortest((0, 0), (mg.nrows - 1, mg.ncols - 1))

    logger.debug(f"Path: {path}")
    print(f"Shortest path has cost {dist}")

    if FANCY_PLOTTING:
        mg.show_mpl(path=path)
