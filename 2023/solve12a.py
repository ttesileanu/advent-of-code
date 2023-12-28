#! /usr/bin/env python
from utils import iterinput, logger

from common12 import find_match_number


if __name__ == "__main__":
    all_n_allowed = []
    for line in iterinput():
        corrupted_row, rle_str = line.split(" ")
        rle = [int(_) for _ in rle_str.split(",")]

        logger.debug(f"{corrupted_row=}, {rle=}")

        n_allowed = find_match_number(corrupted_row, rle)
        all_n_allowed.append(n_allowed)

    print(f"Sum of possible arrangement counts is {sum(all_n_allowed)}")
