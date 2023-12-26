#! /usr/bin/env python
from utils import iterinput, logger
from common9 import Polynomial


if __name__ == "__main__":
    histories = [[int(_) for _ in line.split()] for line in iterinput() if line.strip()]
    logger.debug(f"{histories=}")

    polynomials = [Polynomial.from_sequence(seq) for seq in histories]
    logger.debug(f"{polynomials=}")

    prev_steps_frac = [p(-1) for p in polynomials]

    assert all(_.denominator == 1 for _ in prev_steps_frac)
    prev_steps = [int(_) for _ in prev_steps_frac]

    logger.debug(f"{prev_steps=}")

    s = sum(prev_steps)
    print(f"Sum of extrapolated values is {s}")
