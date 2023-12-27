#! /usr/bin/env python
from utils import loadmatrix

from common10 import FANCY_PLOTTING, find_loop, show_pretty_map


if __name__ == "__main__":
    map = loadmatrix()
    farthest_i, farthest_j, depths = find_loop(map)

    max_depth = depths[(farthest_i, farthest_j)]
    print(f"Number of steps to farthest point {max_depth}")

    if FANCY_PLOTTING:
        show_pretty_map(map, target=(farthest_i, farthest_j), depths=depths)
