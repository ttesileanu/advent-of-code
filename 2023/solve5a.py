#! /usr/bin/env python
from bisect import bisect_left, bisect_right
from collections import defaultdict

from utils import iterinput, logger


class Map:
    def __init__(self):
        self.ranges_start = []
        self.ranges_end = []
        self.deltas = []

    def add_range(self, dest_start: int, src_start: int, length: int):
        idx = bisect_left(self.ranges_start, src_start)

        # ensure no overlaps
        if idx > 0:
            assert self.ranges_end[idx - 1] <= src_start

        src_end = src_start + length
        if idx < len(self.ranges_start):
            assert src_end <= self.ranges_start[idx]

        # insert
        self.ranges_start.insert(idx, src_start)
        self.ranges_end.insert(idx, src_end)
        self.deltas.insert(idx, dest_start - src_start)

    def __getitem__(self, which: int):
        idx = bisect_right(self.ranges_start, which)
        if idx <= 0 or which >= self.ranges_end[idx - 1]:
            # not in map
            return which

        # hit
        return which + self.deltas[idx - 1]

    def __repr__(self) -> str:
        s = "Map(\n"
        for start, end, delta in zip(self.ranges_start, self.ranges_end, self.deltas):
            s += f"[{start:12}, {end:12}): {delta:+12}\n"
        s += ")"
        return s


if __name__ == "__main__":
    seeds = None
    maps = defaultdict(dict)
    state = None

    current_map = None
    for line in iterinput():
        if not line:
            if state is None:
                continue

            # finished a map
            assert state == "map"
            maps[map_ends[0]][map_ends[1]] = current_map
            logger.debug(f"Registered new map {map_ends[0]}-to-{map_ends[1]}:")
            logger.debug(f"{current_map!r}")
            current_map = None
            state = None
            continue

        if state is not None:
            assert state == "map"
            range_spec_str = [_.strip() for _ in line.split(" ")]
            range_spec = [int(_) for _ in range_spec_str if _]
            assert len(range_spec) == 3

            logger.debug(f"Adding {range_spec} to {map_ends} map")
            current_map.add_range(*range_spec)
        else:
            splits = line.split(":")
            assert len(splits) == 2

            if splits[0] == "seeds":
                seeds_str = [_.strip() for _ in splits[1].split(" ")]
                seeds = [int(_) for _ in seeds_str if _]
                logger.debug(f"Found seeds: {seeds}")
            else:
                assert splits[0].endswith("map") and not splits[1]

                map_ends = tuple(splits[0][:-3].strip().split("-to-"))
                assert len(map_ends) == 2

                state = "map"
                logger.debug(f"New map starting, from {map_ends[0]} to {map_ends[1]}")

                current_map = Map()

    if state == "map":
        maps[map_ends[0]][map_ends[1]] = current_map
        logger.debug(f"Registered new map {map_ends[0]}-to-{map_ends[1]}:")
        logger.debug(f"{current_map!r}")

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
