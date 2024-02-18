#! /usr/bin/env python
from collections import defaultdict
from typing import Sequence, Tuple

from utils import iterinput, logger

try:
    import matplotlib.pyplot as plt
    import numpy as np

    FANCY_PLOTTING = True
except ImportError:
    FANCY_PLOTTING = False


Cube = Tuple[int, int, int]
Block = Tuple[Cube, Cube]


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
    blocks = []
    for line in iterinput():
        pos1, pos2 = line.split("~")
        cube1 = tuple(int(_) for _ in pos1.strip().split(","))
        cube2 = tuple(int(_) for _ in pos2.strip().split(","))

        # normalize the coordinates
        cube_min = tuple(min(a, b) for a, b in zip(cube1, cube2))
        cube_max = tuple(max(a, b) for a, b in zip(cube1, cube2))

        blocks.append((cube_min, cube_max))
        logger.debug(f"Found block: {cube_min} ~ {cube_max}")

    logger.info(f"Loaded {len(blocks)} blocks.")

    # by the way we loaded them, we know that cube2[i] >= cube1[i]
    extents = [list(_) for _ in blocks[0]]  # (min, max)
    for block in blocks[1:]:
        for k in range(2):
            cube = block[k]
            for i in range(3):
                extents[0][i] = min(extents[0][i], cube[i])
                extents[1][i] = max(extents[1][i], cube[i])

    logger.info(f"World extents: {extents}.")

    # not necessary, but makes things easier
    assert extents[0][0] == 0
    assert extents[0][1] == 0

    # can't be lower in the z-direction because the ground is at 0
    assert extents[0][2] >= 1

    # start dropping the blocks: they will drop in order of their lowest z
    blocks = sorted(blocks, key=lambda block: block[0][2])
    logger.debug(f"{blocks=}")

    show_blocks(blocks, wait=False)

    # keep track of the largest occupied height for every x, y and which block is there
    # None = ground
    floor = [(extents[1][1] + 1) * [(0, None)] for i in range(extents[1][0] + 1)]
    # keep track of what each block relies on for not falling
    dependencies = defaultdict(set)
    frozen = {None}
    for i, block in enumerate(blocks):
        # where will it fall?
        end_z = 0
        for x in range(block[0][0], block[1][0] + 1):
            for y in range(block[0][1], block[1][1] + 1):
                end_z = max(end_z, floor[x][y][0] + 1)

        start_z = block[0][2]
        assert end_z <= start_z

        # now move it
        logger.debug(f"Block {i} falling from {start_z} to {end_z}")
        height = block[1][2] - block[0][2]
        if end_z < start_z:
            blocks[i] = (
                (block[0][0], block[0][1], end_z),
                (block[1][0], block[1][1], end_z + height),
            )

        # find out dependencies and update floor
        for x in range(block[0][0], block[1][0] + 1):
            for y in range(block[0][1], block[1][1] + 1):
                item = floor[x][y]
                if item[0] == end_z - 1:
                    if item[1] in frozen:
                        frozen.add(i)
                    if item[1] is not None:
                        dependencies[i].add(item[1])

                floor[x][y] = (end_z + height, i)

    assert len(frozen) == len(blocks) + 1
    logger.debug(f"{dependencies=}")

    indispensable = set(
        next(iter(deps)) for deps in dependencies.values() if len(deps) == 1
    )
    logger.debug(f"{indispensable=}")

    dispensable = set(range(len(blocks))).difference(indispensable)
    logger.debug(f"{dispensable=}")

    print(f"{len(dispensable)} bricks can be safely disintegrated.")
    show_blocks(blocks)
