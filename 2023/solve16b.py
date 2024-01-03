#! /usr/bin/env python
import logging
from utils import loadmatrix, logger

from common16 import FANCY_PLOTTING, OpticalSystem


if __name__ == "__main__":
    mat = loadmatrix()

    energized_counts = []
    max_energy = -1
    max_system = None

    # try to insert on left and right
    for i in range(mat.nrows):
        system = OpticalSystem(mat)
        system.insert_ray(i, 0, "W")
        n_energized = system.count_energized()
        logger.debug(f"Ray on row {i} from the left energizes {n_energized}")
        energized_counts.append(n_energized)

        if n_energized > max_energy:
            max_energy = n_energized
            max_system = system

        system = OpticalSystem(mat)
        system.insert_ray(i, mat.ncols - 1, "E")
        n_energized = system.count_energized()
        logger.debug(f"Ray on row {i} from the right energizes {n_energized}")
        energized_counts.append(n_energized)

        if n_energized > max_energy:
            max_energy = n_energized
            max_system = system

    # try to insert on top and bottom
    for j in range(mat.ncols):
        system = OpticalSystem(mat)
        system.insert_ray(0, j, "N")
        n_energized = system.count_energized()
        logger.debug(f"Ray on col {j} from the top energizes {n_energized}")
        energized_counts.append(n_energized)

        if n_energized > max_energy:
            max_energy = n_energized
            max_system = system

        system = OpticalSystem(mat)
        system.insert_ray(mat.nrows - 1, j, "S")
        n_energized = system.count_energized()
        logger.debug(f"Ray on col {j} from the bottom energizes {n_energized}")
        energized_counts.append(n_energized)

        if n_energized > max_energy:
            max_energy = n_energized
            max_system = system

    print(f"Maximum number of energized tiles: {max(energized_counts)}")

    if max_system is not None:
        logger.debug(f"System with maximum energy level:\n{max_system.show()}")
        if logger.isEnabledFor(logging.DEBUG) and FANCY_PLOTTING:
            max_system.show_mpl()
