"""Common definitions for the two phases of day 5."""
from bisect import bisect_left, bisect_right
from collections import defaultdict
from typing import Iterator, List, Union

from utils import logger


class Map:
    def __init__(self):
        self.ranges_start = []
        self.ranges_end = []
        self.deltas = []

    def add_range(self, dest_start: int, src_start: int, length: int):
        assert length > 0
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

    def __getitem__(self, which: Union[int, slice]) -> Union[int, List[slice]]:
        if isinstance(which, int):
            idx = bisect_right(self.ranges_start, which)
            if idx <= 0 or which >= self.ranges_end[idx - 1]:
                # not in map
                return which

            # hit
            return which + self.deltas[idx - 1]
        elif isinstance(which, slice):
            assert which.step is None or which.step == 1
            assert which.start is not None
            assert which.stop is not None

            if which.stop == which.start:
                return []

            results = []
            idx = bisect_right(self.ranges_start, which.start)

            src_start = which.start
            src_end = which.stop
            while src_start < src_end and idx <= len(self.ranges_start):
                # We know that,
                #     ranges_start[idx] > src_start       (if idx < n_ranges)
                #     ranges_start[idx - 1] <= src_start  (if idx > 0)
                #
                # we also know
                #     ranges_end[idx - 1] <= ranges_start[idx]

                if idx > 0 and src_start < self.ranges_end[idx - 1]:
                    # there is overlap with the previous range
                    # need to split src interval
                    start = src_start
                    end = min(src_end, self.ranges_end[idx - 1])
                    delta = self.deltas[idx - 1]
                    results.append((start + delta, end + delta))

                    src_start = end

                if src_start < src_end:
                    # add whatever interval is left before the next range
                    # that does not overlap with the previous range
                    start = src_start
                    if idx < len(self.ranges_start):
                        end = min(src_end, self.ranges_start[idx])
                    else:
                        end = src_end

                    # it could be that ranges_end[idx - 1] = ranges_start[idx]
                    if start < end:
                        results.append((start, end))

                    src_start = end

                idx += 1
                # at this point,   (note the index got incremented!)
                #     either src_start == src_end (and we're done)
                #     or     src_start = self.ranges_start[idx - 1]

            return results
        else:
            raise TypeError(f"Index must be integer or type, got {type(which)!r}")

    def __repr__(self) -> str:
        s = "Map(\n"
        for start, end, delta in zip(self.ranges_start, self.ranges_end, self.deltas):
            s += f"[{start:12}, {end:12}): {delta:+12}\n"
        s += ")"
        return s


def read_seeds_and_maps(it: Iterator[str]):
    seeds = None
    maps = defaultdict(dict)
    state = None

    current_map = None
    for line in it:
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

    return seeds, maps
