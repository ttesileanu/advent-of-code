#! /usr/bin/env python
from common5 import read_seeds_and_maps
from utils import iterinput, logger


if __name__ == "__main__":
    it = iterinput()
    seeds, maps = read_seeds_and_maps(it)

    locations = []
    for seed in seeds:
        logger.debug(f"Tracing seed {seed}...")

        idx = seed
        idx_type = "seed"
        while idx_type != "location":
            possible_maps = maps[idx_type]
            assert len(possible_maps) == 1
            next_idx_type, current_map = next(iter(possible_maps.items()))

            original_idx = idx

            idx = current_map[idx]
            logger.debug(f"...{idx_type} {original_idx} maps to {next_idx_type} {idx}")

            idx_type = next_idx_type

        logger.debug(f"Seed {seed} is in location {idx}")
        locations.append(idx)

    print(f"Lowest location number is {min(locations)}")
