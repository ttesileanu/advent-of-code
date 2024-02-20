import math
import time
from collections import defaultdict
from typing import (
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

from utils import logger, Matrix, PriorityQueue


try:
    import matplotlib.pyplot as plt
    import numpy as np

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False


class Graph:
    Neighbors = List[int]
    Weights = List[int]
    Distances = Dict[int, Union[int, float]]
    Parents = Dict[int, int]

    adj: Dict[int, Tuple[Neighbors, Weights]]

    def __init__(self):
        self.adj = defaultdict(lambda: ([], []))

    def __getitem__(self, idx: int) -> Optional[Tuple[Neighbors, Weights]]:
        """Get the lists of neighbors and weights for the given node.

        This adds the node to the graph if it doesn't already exist.
        """
        return self.adj[idx]

    def add_node(self, idx: int):
        """Add an isolated node."""
        _ = self.adj[idx]

    def add_edge(self, idx1: int, idx2: int, weight: int, allow_multi: bool = False):
        """Add an edge.

        By default, if the edge already exists, its weight is updated. Set `allow_multi`
        to false to avoid the check, which allows for repeated edges between the same
        nodes.

        The nodes are added if necessary.
        """
        self.add_node(idx2)
        if not allow_multi:
            try:
                pos = self[idx1][0].index(idx2)
            except ValueError:
                pos = None

            if pos is not None:
                self[idx1][pos] = weight
                return

        self[idx1][0].append(idx2)
        self[idx1][1].append(weight)

    def shortest(
        self, source: int, target: Optional[int] = None
    ) -> Tuple[Distances, Parents]:
        """Find the shortest paths between the source and one other node, or all nodes.

        Set `target` to stop the iteration once the given target is reached. In this
        case, the `dist` dictionary contains only the `target` key. The `prev`
        dictionary contains keys at least for all the nodes necessary to recreate the
        shortest path from source to target.

        From https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm.

        Returns
        -------
        dist : dict of int
            Distances from source to each node (or just to `target`, if provided).
        prev : dict of int
            Parent nodes for each node for which a parent is known.
        """
        dist = {source: 0}
        prev = {}

        for key in self.adj.keys():
            if key != source:
                dist[key] = math.inf

        q = PriorityQueue()
        q.add_task(source, 0)
        while q:
            u = q.pop_task()
            if target is not None and u == target:
                break

            neighbors, weights = self.adj[u]
            for v, weight in zip(neighbors, weights):
                alt = dist[u] + weight
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u
                    q.add_task(v, alt)

        if target is not None:
            dist = {target: dist[target]}
        return dist, prev


class MatrixGraph:
    mat: Matrix[int]
    graph: Graph
    min_jump: int
    max_jump: int

    Path = List[Tuple[int, int]]

    def __init__(self, m: Matrix[str], *, min_jump: int = 1, max_jump: int = 3):
        self.min_jump = min_jump
        self.max_jump = max_jump

        t0 = time.time()

        self.mat = Matrix([[int(_) for _ in row] for row in m.data])
        self.graph = Graph()
        self._populate_graph()

        t1 = time.time()
        logger.debug(f"Making MatrixGraph took {1000 * (t1 - t0):.1f}ms.")

    def to_node(self, i: int, j: int, dir: Literal["H", "V", "0"]) -> int:
        """Convert matrix location to graph index.

        Parameters
        ----------
        i : int
            Row number.
        j : int
            Column number.
        dir : literal "H", "V", or "0"
            Direction of movement. Can be "H" for horizontal, "V" for vertical, "0" for
            additional node that has 0-cost connections to both H and V planes.
        """
        count = self.nrows * self.ncols
        offset = {"H": 0, "V": 1, "0": 2}[dir] * count
        return i * self.ncols + j + offset

    def to_location(self, idx: int) -> Tuple[int, int, str]:
        """Convert graph index to matrix location and direction.

        Returns
        -------
        i : int
            Row number.
        j : int
            Column number.
        dir : str
            Direction of movement. See `to_node`.
        """
        count = self.nrows * self.ncols
        dir = "HV0"[idx // count]
        idx0 = idx % count
        i = idx0 // self.ncols
        j = idx0 % self.ncols
        return i, j, dir

    def _populate_graph(self):
        self._populate_directional("H")
        self._populate_directional("V")
        self._populate_additional()

    def _populate_additional(self):
        self.graph.add_edge(self.to_node(0, 0, "0"), self.to_node(0, 0, "H"), 0)
        self.graph.add_edge(self.to_node(0, 0, "0"), self.to_node(0, 0, "V"), 0)

        i = self.nrows - 1
        j = self.ncols - 1
        self.graph.add_edge(self.to_node(i, j, "H"), self.to_node(i, j, "0"), 0)
        self.graph.add_edge(self.to_node(i, j, "V"), self.to_node(i, j, "0"), 0)

    def _populate_directional(self, dir: Literal["H", "V"]):
        if dir == "H":
            di = 0
            dj = 1
        elif dir == "V":
            di = 1
            dj = 0

        next_dir = {"H": "V", "V": "H"}[dir]

        for i in range(self.nrows):
            for j in range(self.ncols):
                idx0 = self.to_node(i, j, dir)
                for sign in [-1, 1]:
                    s = 0
                    for k in range(1, self.max_jump + 1):
                        i1 = i + sign * di * k
                        j1 = j + sign * dj * k

                        if 0 <= i1 < self.nrows and 0 <= j1 < self.ncols:
                            s += self.mat[i1, j1]
                            if k >= self.min_jump:
                                idx1 = self.to_node(i1, j1, next_dir)
                                self.graph.add_edge(idx0, idx1, s)

    def shortest(
        self, source: Tuple[int, int], target: Tuple[Union[int, float], int]
    ) -> Tuple[int, Path]:
        """Find the shortest path between two nodes on the "extra" layer."""
        idx0 = self.to_node(*source, dir="0")
        idx1 = self.to_node(*target, dir="0")
        dist_map, prev = self.graph.shortest(idx0, target=idx1)

        if idx0 == idx1:
            return 0, []

        if idx1 not in dist_map or dist_map[idx1] == math.inf:
            return math.inf, []

        path = []
        dirs = []
        u = idx1
        while u in prev:
            i, j, dir = self.to_location(u)
            path.append((i, j))
            dirs.append(dir)
            u = prev[u]

        assert u == idx0
        i, j, dir = self.to_location(u)
        assert dir[0] == "0"
        assert not any(_ == "0" for _ in dirs[1:])

        # don't actually want the extra-plane nodes in the path
        path = path[:0:-1]
        dist = dist_map[idx1]

        return dist, path

    @property
    def nrows(self) -> int:
        return self.mat.nrows

    @property
    def ncols(self) -> int:
        return self.mat.ncols

    def __repr__(self) -> str:
        s = str(self.mat)
        assert "Matrix" in s
        s = s.replace("Matrix", "MatrixGraph")
        return s

    if FANCY_PLOTTING:

        def show_mpl(
            self, path: Optional[Path] = None, ax: Optional[plt.Axes] = None
        ) -> plt.Axes:
            if ax is None:
                _, ax = plt.subplots(figsize=(4, 4))
            ax.imshow(self.mat.data, cmap="Reds")

            if path is not None:
                npath = np.asarray(path)
                ax.plot(npath[:, 1], npath[:, 0], c="C0", lw=1.0)

            plt.show()
            return ax
