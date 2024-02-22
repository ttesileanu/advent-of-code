import math
from typing import Dict, List, Optional, Set, Tuple

from utils import logger, Matrix, PriorityQueue


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


def show_matrix(
    mat: Matrix[str],
    wait: bool = True,
    figsize: float = 7.0,
    path: Optional[List[Tuple[int, int]]] = None,
):
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

    if path is not None:
        p = np.asarray(path)
        x = p[:, 1]
        y = p[:, 0]
        ax.plot(x, y, lw=4, ls=":")

    if wait:
        plt.show()
    return fig, ax


class IntersectionGraph:
    nodes: List[Tuple[int, int]]
    mat_to_node: Dict[Tuple[int, int], int]
    adj: List[Dict[int, int]]
    paths: Dict[Tuple[int, int], List[Tuple[int, int]]]
    slopes: bool

    def __init__(self, mat: Matrix[str], slopes: bool = True):
        self.nodes = []
        self.mat_to_node = {}
        self.paths = {}
        self.adj = []
        self.slopes = slopes
        self._build_nodes(mat)
        self._build_adj(mat)

    def _build_nodes(self, mat: Matrix[str]):
        # find start and end intersections + add slopes (if needed)
        assert mat.data[0].count(GROUND) == 1
        assert mat.data[-1].count(GROUND) == 1
        start = (0, mat.data[0].index(GROUND))
        end = (mat.nrows - 1, mat.data[-1].index(GROUND))

        if self.slopes:
            n_slopes = sum(sum(1 if _ in SLOPES else 0 for _ in r) for r in mat.data)
            logger.debug(f"{n_slopes=}")

            # add appropriate slopes at start and end points
            mat[start[0] + 1, start[1]] = SLOPE_DOWN
            mat[end[0] - 1, end[1]] = SLOPE_DOWN
        else:
            for i in range(mat.nrows):
                for j in range(mat.ncols):
                    if mat[i, j] in SLOPES:
                        mat[i, j] = GROUND

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
                        if self.slopes:
                            assert all(_ in SLOPES for _ in neighbors)

        logger.info(
            f"There are {len(self.nodes)} intersections on the map "
            "(including start and end)."
        )
        logger.debug(f"nodes={self.nodes}")
        assert self.nodes[0] == start
        assert self.nodes[-1] == end

    def _build_adj(self, mat: Matrix[str]):
        for _, source in enumerate(self.nodes):
            targets = {}
            neighbors = mat.iterneighbors(*source, diagonals=False)
            for neigh in neighbors:
                if self.slopes:
                    is_path = (
                        mat[neigh] == SLOPE_RIGHT
                        and neigh == (source[0], source[1] + 1)
                        or mat[neigh] == SLOPE_LEFT
                        and neigh == (source[0], source[1] - 1)
                        or mat[neigh] == SLOPE_UP
                        and neigh == (source[0] - 1, source[1])
                        or mat[neigh] == SLOPE_DOWN
                        and neigh == (source[0] + 1, source[1])
                    )
                else:
                    is_path = mat[neigh] != FOREST
                if is_path:
                    target_pos, length = self._trace(mat, source, neigh)
                    target = self.mat_to_node[target_pos]
                    targets[target] = length

            self.adj.append(targets)

        logger.debug(f"adj={self.adj}")

    def _trace(
        self, mat: Matrix[str], source: Tuple[int, int], to: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], int]:
        visited = {source}
        path = [source]
        pos = to
        while True:
            neighbors = mat.iterneighbors(*pos, diagonals=False)
            potentials = [n for n in neighbors if mat[n] != FOREST]
            if len(potentials) == 1:
                assert pos[0] == 0 or pos[0] == mat.nrows - 1
                break
            elif len(potentials) == 2:
                visited.add(pos)
                path.append(pos)
                pos_candidates = [n for n in potentials if n not in visited]
                assert len(pos_candidates) == 1
                pos = pos_candidates[0]
            else:
                assert len(potentials) > 2
                assert pos in self.nodes
                break

        self.paths[self.mat_to_node[source], self.mat_to_node[pos]] = path
        return pos, len(visited)

    def longest(self, start: int, end: int) -> Tuple[int, List[Tuple[int, int]]]:
        if self.slopes:
            length, path_nodes = self._longest_dag(start, end)
        else:
            length, path_nodes = self._longest_no_slopes(start, end)

        path = []
        for n1, n2 in zip(path_nodes[:-1], path_nodes[1:]):
            path.extend(self.paths[n1, n2])

        return length, path

    def _longest_dag(self, start: int, end: int) -> Tuple[int, List[int]]:
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

        path_nodes = []
        node = end
        while node in prev:
            path_nodes.append(node)
            node = prev[node]
        assert node == start
        path_nodes.append(node)
        path_nodes = path_nodes[::-1]

        return length, path_nodes

    def _search(
        self,
        source: int,
        target: int,
        prev_length: int,
        prev_path: List[int],
        prev_visited: Set[int],
    ):
        candidates = self.adj[source]
        for node, edge_length in candidates.items():
            if node in prev_visited:
                continue

            length = prev_length + edge_length
            path = prev_path + [node]
            if node == target:
                if length > self._longest[0]:
                    self._longest = (length, path)
            else:
                visited = set(prev_visited)
                visited.add(node)
                self._search(node, target, length, path, visited)

    def _longest_no_slopes(self, start: int, end: int) -> Tuple[int, List[int]]:
        self._longest = (0, [])
        self._search(start, end, 0, [start], set([start]))

        return self._longest
