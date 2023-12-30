#! /usr/bin/env python
from utils import iterinput, logger


def HASH(s: str) -> int:
    h = 0
    for c in s:
        h += ord(c)
        h = (h * 17) % 256

    return h


if __name__ == "__main__":
    it = iterinput()
    line = ""
    while not line:
        line = next(it)

    assert line
    for extra in it:
        assert not extra

    steps = line.split(",")
    steps_str = "\n".join(steps)
    logger.debug(f"Input steps: \n{steps_str}")

    HASHes = []
    for step in steps:
        HASHes.append(HASH(step))

    logger.debug(f"{HASHes=}")

    print(f"Sum of HASH results is {sum(HASHes)}")
