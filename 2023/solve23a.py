#! /usr/bin/env python
from utils import loadmatrix, logger

from common23 import IntersectionGraph, show_matrix

if __name__ == "__main__":
    mat = loadmatrix()
    logger.debug(f"{mat=}")

    # Finding the longest non-intersecting path in a graph is NP hard, so let's try to
    # find a trick.

    # A key observation here is that the map is organized more like a maze, with a 1d
    # path snaking around such that at every position there are only two ways to go:
    # one backwards (which you can't go to because you're not allowed to repeat
    # positions) and one forward. There are ~30 branching points on the map, and given
    # the previous observation, once you start in a certain direction from a branching
    # point, there is only one path that can be taken until you reach another branching.
    # This means that the path from start to end can be modeled a non-intersecting walk
    # on a graph in which the nodes are branching points on the map and the edge weights
    # are given by the number of steps needed to walk from one branching point to
    # another. Finding the longest path on the map is equivalent to finding the longest
    # path on this graph.

    # Now, that is still an NP-hard problem, so this might not help directly. Let us
    # assume the graph contains no cycles, so it is a directed acyclic graph (DAG).

    g = IntersectionGraph(mat)

    length, path = g.longest(0, len(g.nodes) - 1)
    logger.debug(f"Longest path: {path}")
    print(f"Longest hike has {length} steps.")
    show_matrix(mat, path=path)
