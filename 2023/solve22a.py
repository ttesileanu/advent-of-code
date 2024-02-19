#! /usr/bin/env python
from typing import Sequence

from utils import iterinput, logger

from common22 import Block, drop_and_count_deps, load_blocks

try:
    import matplotlib.pyplot as plt
    import numpy as np

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False


def show_blocks(blocks: Sequence[Block], wait: bool = True):
    if not FANCY_PLOTTING:
        return

    blocks = np.asarray(blocks)  # N x 2 x 3
    all_cubes = np.reshape(blocks, (-1, 3))
    minimums = np.min(all_cubes, axis=0)
    maximums = np.max(all_cubes, axis=0)

    counts = maximums - minimums + 1
    filled = np.zeros(counts)
    for cube1, cube2 in blocks:
        i0 = min(cube1[0], cube2[0])
        i1 = max(cube1[0], cube2[0])

        j0 = min(cube1[1], cube2[1])
        j1 = max(cube1[1], cube2[1])

        k0 = min(cube1[2], cube2[2])
        k1 = max(cube1[2], cube2[2])

        filled[i0 : i1 + 1, j0 : j1 + 1, k0 : k1 + 1] = 1

    dim1, dim2, dim3 = filled.shape
    dim = (dim1 + dim2) // 2

    fig = plt.figure(figsize=((1 + dim / dim3 * 10), 5))
    ax = fig.add_subplot(projection="3d")
    ax.voxels(filled=filled)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    if wait:
        plt.show()
    return ax


if __name__ == "__main__":
    blocks = load_blocks(iterinput())
    show_blocks(blocks, wait=False)

    dependencies = drop_and_count_deps(blocks).dependencies
    logger.debug(f"{dependencies=}")

    indispensable = set(
        next(iter(deps)) for deps in dependencies.values() if len(deps) == 1
    )
    logger.debug(f"{indispensable=}")

    dispensable = set(range(len(blocks))).difference(indispensable)
    logger.debug(f"{dispensable=}")

    print(f"{len(dispensable)} bricks can be safely disintegrated.")
    show_blocks(blocks)
