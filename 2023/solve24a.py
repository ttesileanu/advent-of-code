#! /usr/bin/env python
from fractions import Fraction
from typing import Optional

from utils import iterinput, logger
from common24 import Array, Hailstone


BOUNDS = [200_000_000_000_000, 400_000_000_000_000]


def intersect2d_fwd(
    stone1: Hailstone, stone2: Hailstone, check_bounds: bool = True
) -> Optional[Array]:
    # ignoring z coordinate and looking only at positive times
    # x = p1 + t1 * v1 = p2 + t2 * v2
    #    -> v1 * t1 - v2 * t2 = p2 - p1
    # In matrix form:
    #   [ v1x   -v2x ] [ t1 ]    [ p2x - p1x ]
    #   [ v1y   -v2y ] [ t2 ]  = [ p2y - p1y ]

    logger.debug(f"A: {stone1}")
    logger.debug(f"B: {stone2}")

    v1x, v1y, _ = stone1.velocity
    v2x, v2y, _ = stone2.velocity
    dpx = stone2.position[0] - stone1.position[0]
    dpy = stone2.position[1] - stone1.position[1]

    det = v1y * v2x - v1x * v2y
    det1 = dpy * v2x - dpx * v2y
    det2 = v1x * dpy - v1y * dpx
    if det != 0:
        # unique solution
        t1 = Fraction(det1, det)
        t2 = Fraction(det2, det)
        if t1 < 0 or t2 < 0:
            if t1 < 0 and t2 < 0:
                logger.debug("    Paths crossed in the past for both hailstones.")
            elif t1 < 0:
                logger.debug("    Paths crossed in the past for both hailstone A.")
            else:
                logger.debug("    Paths crossed in the past for both hailstone B.")
            return None
        else:
            cross1 = stone1.position[:2] + t1 * stone1.velocity[:2]
            cross2 = stone2.position[:2] + t2 * stone2.velocity[:2]
            assert all(cross1 == cross2)

            if check_bounds:
                is_inside = all(BOUNDS[0] <= _ <= BOUNDS[1] for _ in cross1)
                inside_str = ["out", "in"][is_inside] + "side"

                logger.debug(f"    Paths will cross {inside_str} test area.")
                return cross1 if is_inside else None
            else:
                logger.debug("    Paths will cross. (no bounds check, by request)")
                return cross1
    else:
        if det1 != 0 or det2 != 0:
            # no solution
            logger.debug("    Paths are parallel; they never intersect.")
        else:
            raise NotImplementedError(
                "Hailstones with identical trajectories not supported"
            )


if __name__ == "__main__":
    hailstones = []
    for line in iterinput():
        pos_str, vel_str = line.split("@")
        pos = [int(_) for _ in pos_str.split(",", maxsplit=2)]
        vel = [int(_) for _ in vel_str.split(",", maxsplit=2)]

        hailstones.append(Hailstone(Array(pos), Array(vel)))

    n = len(hailstones)
    logger.info(f"There are {len(hailstones)} hailstones.")
    logger.debug(f"{hailstones=}")

    count = 0
    for i in range(n):
        stone1 = hailstones[i]
        for j in range(i + 1, n):
            stone2 = hailstones[j]
            x = intersect2d_fwd(stone1, stone2)
            if x is not None:
                count += 1

    print(f"There are {count} intersection in test area.")
