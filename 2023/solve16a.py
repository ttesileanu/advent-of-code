#! /usr/bin/env python
import logging
from utils import loadmatrix, logger

from common16 import FANCY_PLOTTING, OpticalSystem


if __name__ == "__main__":
    mat = loadmatrix()

    system = OpticalSystem(mat)

    # add a ray at port "W" of cell 0, 0; i.e., coming from the West, going East
    # then propagate the ray
    logger.debug(f"System before ray:\n{system.show()}")
    system.insert_ray(0, 0, "W")
    logger.debug(f"System after ray:\n{system.show()}")

    print(f"Number of energized tiles: {system.count_energized()}")

    if logger.isEnabledFor(logging.DEBUG) and FANCY_PLOTTING:
        system.show_mpl()
