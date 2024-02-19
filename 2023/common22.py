from collections import defaultdict
from types import SimpleNamespace
from typing import Iterator, List, Tuple

from utils import logger

Cube = Tuple[int, int, int]
Block = Tuple[Cube, Cube]


def load_blocks(it: Iterator) -> List[Block]:
    blocks = []
    for line in it:
        pos1, pos2 = line.split("~")
        cube1 = tuple(int(_) for _ in pos1.strip().split(","))
        cube2 = tuple(int(_) for _ in pos2.strip().split(","))

        # normalize the coordinates
        cube_min = tuple(min(a, b) for a, b in zip(cube1, cube2))
        cube_max = tuple(max(a, b) for a, b in zip(cube1, cube2))

        blocks.append((cube_min, cube_max))
        logger.debug(f"Found block: {cube_min} ~ {cube_max}")

    logger.info(f"Loaded {len(blocks)} blocks.")
    return blocks


def find_extents(blocks: List[Block]) -> List[List[int]]:
    # by the way we loaded them, we know that cube2[i] >= cube1[i]
    extents = [list(_) for _ in blocks[0]]  # (min, max)
    for block in blocks[1:]:
        for k in range(2):
            cube = block[k]
            for i in range(3):
                extents[0][i] = min(extents[0][i], cube[i])
                extents[1][i] = max(extents[1][i], cube[i])

    logger.info(f"World extents: {extents}.")
    return extents


def drop_and_count_deps(blocks: List[Block]) -> SimpleNamespace:
    extents = find_extents(blocks)

    # not necessary, but makes things easier
    assert extents[0][0] == 0
    assert extents[0][1] == 0

    # can't be lower in the z-direction because the ground is at 0
    assert extents[0][2] >= 1

    # start dropping the blocks: they will drop in order of their lowest z
    blocks.sort(key=lambda block: block[0][2])
    logger.debug(f"{blocks=}")

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
    res = SimpleNamespace(dependencies=dependencies, floor=floor)
    return res
