#! /usr/bin/env python
import sys
import re
from tqdm import tqdm

from typing import Tuple, Optional, List


def l1_norm(x1: Tuple[int, int], x2: Tuple[int, int]) -> int:
    return abs(x1[0] - x2[0]) + abs(x1[1] - x2[1])


def slice_1d(
    origin: Tuple[int, int], radius: int, y: int, clip: Tuple[int, int]
) -> Optional[Tuple[int, int]]:
    """Given a sensor location (`origin`) and a `radius`, find the slice of its
    coverage along row `y`, clipping all coordinates to the range `clip`.

    If there is no coverage in row `y`, returns `None`. The returned tuple has the
    starting and ending `x` coordinates of the coverage, *both inclusive*.
    """
    assert y >= clip[0] and y <= clip[1]
    assert origin[0] >= clip[0] and origin[0] <= clip[1]
    assert origin[1] >= clip[0] and origin[1] <= clip[1]
    
    r_slice = radius - abs(y - origin[1])
    if r_slice < 0:
        return None
        
    return (max(origin[0] - r_slice, clip[0]), min(origin[0] + r_slice, clip[1]))


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
print(f"reading from {fname}... ", end="")
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

print("done.")

# max_coord = 20
max_coord = 4_000_000
target = None
for slice_y in tqdm(range(0, max_coord + 1)):
    slices = []
    for sensor, radius in zip(sensors, radii):
        crt_slice = slice_1d(sensor, radius, slice_y, (0, max_coord))
        if crt_slice is not None:
          slices.append(crt_slice)

    coverage = coalesce(slices)
    first = coverage[0]
    if first[0] <= 0 and first[1] >= max_coord:
        # this slice is completely covered
        continue
    else:
        assert target is None, "more than one possible beacon position!"
        # we found a beacon position!
        if first[0] > 0:
            assert first[0] == 1, "more than one possible beacon position!"
            target = (0, slice_y)
        else:
            target = first[1] + 1, slice_y
            if target[0] < max_coord:
                assert len(coverage) > 1
                assert coverage[1][0] == target[0] + 1
    
print(f"beacon at {target}")

multiplier = 4_000_000
freq = multiplier * target[0] + target[1]
print(f"beacon tuning frequency: {freq}")
