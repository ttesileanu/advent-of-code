#! /usr/bin/env python
from utils import loadmatrix, logger

from common11 import expanded_distance, parse_image


EXPANSION_FACTOR = 1000000


if __name__ == "__main__":
    img = loadmatrix()
    logger.debug(f"{img}")

    galaxy_info = parse_image(img)
    logger.debug(
        f"{len(galaxy_info.galaxies)} galaxies, "
        f"{len(galaxy_info.empty_rows)} empty rows, "
        f"{len(galaxy_info.empty_cols)} empty cols"
    )
    logger.debug(f"{galaxy_info}")

    pair_distances = []
    for i, a in enumerate(galaxy_info.galaxies):
        for j, b in enumerate(galaxy_info.galaxies[i + 1 :], i + 1):
            d = expanded_distance(
                a,
                b,
                galaxy_info.empty_rows,
                galaxy_info.empty_cols,
                factor=EXPANSION_FACTOR,
            )
            pair_distances.append(d)
            logger.debug(f"distance between galaxy {i} and galaxy {j} is {d}")

    s = sum(pair_distances)
    print(f"The sum of the lengths of all paired shortest paths is {s}")
