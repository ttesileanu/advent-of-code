#! /usr/bin/env python
import math
from typing import Dict, List, Tuple

from utils import loadmatrix, logger, Matrix, PriorityQueue

GROUND = "."
FOREST = "#"
SLOPE_RIGHT = ">"
SLOPE_LEFT = "<"
SLOPE_UP = "^"
SLOPE_DOWN = "v"

SLOPES = SLOPE_LEFT + SLOPE_RIGHT + SLOPE_DOWN + SLOPE_UP

try:
    import matplotlib.pyplot as plt
    import numpy as np

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False


def show_matrix(mat: Matrix[str], wait: bool = True, figsize: float = 7.0):
    fig, ax = plt.subplots(figsize=(figsize, figsize))
    m = np.asarray(mat.data) != "#"
    ax.imshow(m, cmap="gray")

    fontsize = figsize / mat.nrows * 72 * 1.2
    for i in range(mat.nrows):
        for j in range(mat.ncols):
            ch = mat[i, j]
            if ch in SLOPES:
                ax.text(
                    j,
                    i,
                    ch,
                    color="red",
                    ha="center",
                    va="center",
                    fontweight="bold",
                    fontsize=fontsize,
                )

    if wait:
        plt.show()
    return fig, ax


class IntersectionGraph:
    nodes: List[Tuple[int, int]]
    mat_to_node: Dict[Tuple[int, int], int]
    adj: List[Dict[int, int]]

    def __init__(self, mat: Matrix[str]):
        self.nodes = []
        self.mat_to_node = {}
        self.adj = []
        self._build_nodes(mat)
        self._build_adj(mat)

    def _build_nodes(self, mat: Matrix[str]):
        # check that the map is a maze with a relatively small number of intersections
        for i in range(mat.nrows):
            for j in range(mat.ncols):
                if mat[i, j] != FOREST:
                    neighbors = mat.iterneighborvalues(i, j, diagonals=False)
                    n_paths = sum(1 if neigh != FOREST else 0 for neigh in neighbors)
                    if n_paths > 2 or i == 0 or i == mat.nrows - 1:
                        pos = (i, j)
                        self.mat_to_node[pos] = len(self.nodes)
                        self.nodes.append(pos)
                        assert all(_ in SLOPES for _ in neighbors)

        logger.info(
            f"There are {len(self.nodes)} intersections on the map "
            "(including start and end)."
        )
        logger.debug(f"nodes={self.nodes}")

    def _build_adj(self, mat: Matrix[str]):
        for _, source in enumerate(self.nodes):
            targets = {}
            neighbors = mat.iterneighbors(*source, diagonals=False)
            for neigh in neighbors:
                if (
                    mat[neigh] == SLOPE_RIGHT
                    and neigh == (source[0], source[1] + 1)
                    or mat[neigh] == SLOPE_LEFT
                    and neigh == (source[0], source[1] - 1)
                    or mat[neigh] == SLOPE_UP
                    and neigh == (source[0] - 1, source[1])
                    or mat[neigh] == SLOPE_DOWN
                    and neigh == (source[0] + 1, source[1])
                ):
                    target_pos, length = self._trace(mat, source, neigh)
                    target = self.mat_to_node[target_pos]
                    targets[target] = length

            self.adj.append(targets)

        logger.debug(f"adj={self.adj}")

    def _trace(
        self, mat: Matrix[str], source: Tuple[int, int], to: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], int]:
        visited = {source}
        pos = to
        while True:
            neighbors = mat.iterneighbors(*pos, diagonals=False)
            potentials = [n for n in neighbors if mat[n] != FOREST]
            if len(potentials) == 1:
                assert pos[0] == 0 or pos[0] == mat.nrows - 1
                break
            elif len(potentials) == 2:
                visited.add(pos)
                pos_candidates = [n for n in potentials if n not in visited]
                assert len(pos_candidates) == 1
                pos = pos_candidates[0]
            else:
                assert len(potentials) > 2
                assert pos in self.nodes
                break

        return pos, len(visited)

    def longest(self, start: int, end: int) -> int:
        weights = {start: 0}
        prev = {}

        q = PriorityQueue()
        for i in range(len(self.nodes)):
            if i != start:
                weights[i] = math.inf
            q.add_task(i, weights[i])

        while q:
            u = q.pop_task()
            for v, weight in self.adj[u].items():
                alt = weights[u] - weight
                if alt < weights[v]:
                    weights[v] = alt
                    prev[v] = u
                    q.add_task(v, alt)

        length = -weights[end]
        return length


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

    assert mat.data[0].count(GROUND) == 1
    assert mat.data[-1].count(GROUND) == 1
    start = (0, mat.data[0].index(GROUND))
    end = (mat.nrows - 1, mat.data[-1].index(GROUND))

    n_slopes = sum(sum(1 if _ in SLOPES else 0 for _ in row) for row in mat.data)
    logger.debug(f"{n_slopes=}")

    # add appropriate slopes at start and end points
    mat[start[0] + 1, start[1]] = SLOPE_DOWN
    mat[end[0] - 1, end[1]] = SLOPE_DOWN

    g = IntersectionGraph(mat)
    assert g.nodes[0] == start
    assert g.nodes[-1] == end

    length = g.longest(0, len(g.nodes) - 1)
    print(f"Longest hike has {length} steps.")
    show_matrix(mat)
