#! /usr/bin/env python
import sys
import re

from typing import Tuple, Optional, List


def l1_norm(x1: Tuple[int, int], x2: Tuple[int, int]) -> int:
    return abs(x1[0] - x2[0]) + abs(x1[1] - x2[1])


def slice_1d(origin: Tuple[int, int], radius: int, y: int) -> Optional[Tuple[int, int]]:
    """Given a sensor location (`origin`) and a `radius`, find the slice of its
    coverage along row `y`.

    If there is no coverage in row `y`, returns `None`. The returned tuple has the
    starting and ending `x` coordinates of the coverage, *both inclusive*.
    """
    r_slice = radius - abs(y - origin[1])
    if r_slice < 0:
        return None
        
    return (origin[0] - r_slice, origin[0] + r_slice)


def coalesce(slices: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Coalesce a set of potentially overlapping slices into disjoint and non-touching
    intervals.
    """
    slices = sorted(slices)
    res = []
    for crt_slice in slices:
        if len(res) == 0 or crt_slice[0] > res[-1][1] + 1:
            res.append(crt_slice)
        else:
            # everything is sorted by first index, so we only need to worry about right
            # edge
            res[-1] = (res[-1][0], max(res[-1][1], crt_slice[1]))

    return res


fname = "input15" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    sensors = []
    beacons = []
    radii = []   # in L1 norm

    pattern = re.compile(
        r"Sensor at x=(-?\d+), y=(-?\d+): closest beacon is at x=(-?\d+), y=(-?\d+)"
    )
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        parse = pattern.fullmatch(line)
        assert parse is not None, f"cannot parse entry: {line}"
        
        sensor_x, sensor_y, beacon_x, beacon_y = [int(_) for _ in parse.groups()]
        sensors.append((sensor_x, sensor_y))
        beacons.append((beacon_x, beacon_y))
        radii.append(l1_norm(sensors[-1], beacons[-1]))

# slice_y = 10
slice_y = 2_000_000
slices = []
for sensor, radius in zip(sensors, radii):
    crt_slice = slice_1d(sensor, radius, slice_y)
    if crt_slice is not None:
      slices.append(crt_slice)

coverage = coalesce(slices)

print(coverage)

beacons_on_slice = set(_ for _ in beacons if _[1] == slice_y)
count = 0
for interval in coverage:
    length = interval[1] - interval[0] + 1
    for beacon in beacons_on_slice:
        if beacon[0] >= interval[0] and beacon[0] <= interval[1]:
            print(f"beacon {beacon} on interval {interval}")
            length -= 1

    count += length
    
print(f"number of covered positions: {count}")
