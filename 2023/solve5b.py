#! /usr/bin/env python
from common5 import read_seeds_and_maps
from utils import iterinput, logger, args


def test_interval_map(map, interval):
    image_intervals = map[slice(*interval)]
    image = []
    for crt_interval in image_intervals:
        image.extend(range(*crt_interval))

    expected_image = []
    for x in range(*interval):
        expected_image.append(map[x])

    if image != expected_image:
        raise RuntimeError(f"Mismatch: image: \n{image}, expected: \n{expected_image}")


def test_interval_maps(intervals, maps):
    for map_it in maps.items():
        assert len(map_it[1]) == 1
        map_start = map_it[0]

        map_tuple = next(iter(map_it[1].items()))
        map_end = map_tuple[0]

        logger.debug(f"testing {map_start}-to-{map_end}")
        map = map_tuple[1]
        for interval in intervals:
            test_interval_map(map, interval)


if __name__ == "__main__":
    it = iterinput()
    seeds, maps = read_seeds_and_maps(it)
    intervals = [
        (start, start + length) for start, length in zip(seeds[::2], seeds[1::2])
    ]

    if args.tests:
        test_interval_maps(intervals, maps)
    else:
        idx_type = "seed"
        while idx_type != "location":
            logger.debug(f"{idx_type} intervals: {intervals}")

            possible_maps = maps[idx_type]
            assert len(possible_maps) == 1
            next_idx_type, current_map = next(iter(possible_maps.items()))

            next_intervals = []
            for interval in intervals:
                next_intervals.extend(current_map[slice(*interval)])

            intervals = next_intervals
            idx_type = next_idx_type

        logger.debug(f"{idx_type} intervals: {intervals}")
        min_location = min(min(_) for _ in intervals)

        print(f"Lowest location number: {min_location}")
