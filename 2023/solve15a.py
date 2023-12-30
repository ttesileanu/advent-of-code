#! /usr/bin/env python
from utils import logger

from common15 import HASH, read_steps


if __name__ == "__main__":
    steps = read_steps()

    HASHes = []
    for step in steps:
        HASHes.append(HASH(step))

    logger.debug(f"{HASHes=}")

    print(f"Sum of HASH results is {sum(HASHes)}")
