#! /usr/bin/env python
from utils import iterinput, logger
from common9 import Polynomial


if __name__ == "__main__":
    histories = [[int(_) for _ in line.split()] for line in iterinput() if line.strip()]
    logger.debug(f"{histories=}")

    polynomials = [Polynomial.from_sequence(seq) for seq in histories]
    logger.debug(f"{polynomials=}")

    next_steps_frac = [p(len(h)) for h, p in zip(histories, polynomials)]

    assert all(_.denominator == 1 for _ in next_steps_frac)
    next_steps = [int(_) for _ in next_steps_frac]

    logger.debug(f"{next_steps=}")

    s = sum(next_steps)
    print(f"Sum of extrapolated values is {s}")
