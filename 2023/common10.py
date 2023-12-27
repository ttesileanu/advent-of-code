from collections import deque
from typing import Dict, Optional, Sequence, Tuple

try:
    import numpy as np
    import matplotlib.pyplot as plt

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False

from utils import logger, Matrix


if FANCY_PLOTTING:
    PRETTY_DICT = {
        ".": [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        "-": [[0, 0, 0], [1, 1, 1], [0, 0, 0]],
        "|": [[0, 1, 0], [0, 1, 0], [0, 1, 0]],
        "L": [[0, 1, 0], [0, 1, 1], [0, 0, 0]],
        "J": [[0, 1, 0], [1, 1, 0], [0, 0, 0]],
        "7": [[0, 0, 0], [1, 1, 0], [0, 1, 0]],
        "F": [[0, 0, 0], [0, 1, 1], [0, 1, 0]],
        "S": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
    }

    def pretty_map(
        map: Matrix,
        target: Optional[Tuple[int, int]] = None,
        depths: Optional[Dict[Tuple[int, int], int]] = None,
        tags: Optional[Matrix] = None,
    ) -> np.ndarray:
        v = np.zeros((3 * map.nrows, 3 * map.ncols, 3))
        max_depth = None if depths is None else max(depths.values())
        for i, row in enumerate(map.data):
            si = 3 * i
            for j, elem in enumerate(row):
                sj = 3 * j
                if tags is not None:
                    tag = tags[i, j]
                else:
                    tag = " "

                if elem == "S":
                    color = np.asarray([1, 0, 0])
                elif target is not None and target == (i, j):
                    color = np.asarray([0, 0, 1])
                elif depths is not None and (i, j) in depths:
                    depth = depths[(i, j)]
                    g = 0.4 + 0.4 * depth / max_depth
                    color = np.asarray([0, g, 0])
                else:
                    color = np.asarray([1, 1, 1])

                pretty_elem = np.asarray(PRETTY_DICT[elem])
                elem_sq = color[None, None, :] * pretty_elem[..., None]

                if tag == "I":
                    f = np.asarray([0.8, 0.8, 1.2])[None, None, :]
                    c = np.asarray([-0.05, 0.05, 0.3])[None, None, :]
                    elem_sq = np.clip(elem_sq * f + c, 0, 1)
                elif tag == "O":
                    f = np.asarray([1.2, 0.8, 0.8])[None, None, :]
                    c = np.asarray([0.3, -0.05, 0.05])[None, None, :]
                    elem_sq = np.clip(elem_sq * f + c, 0, 1)

                v[si : si + 3, sj : sj + 3] = elem_sq

        return v

    def show_pretty_map(
        map: Matrix,
        ax: Optional[plt.Axes] = None,
        target: Optional[Tuple[int, int]] = None,
        depths: Optional[Dict[Tuple[int, int], int]] = None,
        tags: Optional[Matrix] = None,
    ) -> plt.Axes:
        if ax is None:
            _, ax = plt.subplots()

        ax.imshow(
            pretty_map(map, target=target, depths=depths, tags=tags),
            extent=(-0.5, map.ncols - 0.5, map.nrows - 0.5, -0.5),
        )
        plt.show()
        return ax


if not FANCY_PLOTTING:

    def show_pretty_map(*args, **kwargs):
        raise NotImplementedError("show_pretty_map not available without matplotlib")


def get_pipe_neighbors(map: Matrix, i: int, j: int) -> Sequence[Tuple[int, int]]:
    elem = map[i, j]
    neighbors = []

    if i > 0 and elem in "|LJS" and map[i - 1, j] in "|7F":
        neighbors.append((i - 1, j))
    if i + 1 < map.nrows and elem in "|7FS" and map[i + 1, j] in "|LJ":
        neighbors.append((i + 1, j))
    if j > 0 and elem in "-7JS" and map[i, j - 1] in "-LF":
        neighbors.append((i, j - 1))
    if j + 1 < map.ncols and elem in "-LFS" and map[i, j + 1] in "-7J":
        neighbors.append((i, j + 1))

    assert len(neighbors) <= 2
    return neighbors


def bfs(map: Matrix, i: int, j: int) -> Tuple[int, int, Dict[Tuple[int, int], int]]:
    """Run BFS, return last visited node and dict of depths."""
    visited_depths = {(i, j): 0}
    q = deque([(i, j, 0)])
    while q:
        i, j, depth = q.popleft()
        neighbors = get_pipe_neighbors(map, i, j)
        for ni, nj in neighbors:
            if (ni, nj) not in visited_depths:
                visited_depths[(ni, nj)] = depth + 1
                q.append((ni, nj, depth + 1))

    return i, j, visited_depths


def find_loop(map: Matrix) -> Tuple[int, int, Dict[Tuple[int, int], int]]:
    # we basically need to do a BDF search starting at the "S", and the last node
    # visited is the farthest
    si = sj = None
    for i, row in enumerate(map.data):
        for j, elem in enumerate(row):
            if elem == "S":
                si = i
                sj = j
                break

    assert si is not None
    assert sj is not None

    res = bfs(map, si, sj)
    logger.debug(f"Farthest point located at {res[:2]}.")
    return res
