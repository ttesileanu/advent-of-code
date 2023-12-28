#! /usr/bin/env python
from itertools import product
from typing import Iterator, List

from utils import iterinput, logger

from common12 import find_match_number


def possible_arrangements(s: str) -> Iterator[str]:
    unknown_idxs = [i for i in range(len(s)) if s[i] == "?"]
    for choice in product(".#", repeat=len(unknown_idxs)):
        l = list(s)
        for i, c in zip(unknown_idxs, choice):
            l[i] = c

        yield "".join(l)


def rle_encode(s: str) -> List[int]:
    code = []
    count = 0
    for c in s:
        if c == "#":
            count += 1
        elif c == ".":
            if count > 0:
                code.append(count)
                count = 0
        else:
            raise ValueError(f"Unsupported character '{c}'")

    if count > 0:
        code.append(count)
    return code


if __name__ == "__main__":
    all_n_allowed = []
    for line in iterinput():
        corrupted_row, rle_str = line.split(" ")
        rle = [int(_) for _ in rle_str.split(",")]

        logger.debug(f"{corrupted_row=}, {rle=}")

        n_allowed = find_match_number(corrupted_row, rle)

        allowed = []
        for row in possible_arrangements(corrupted_row):
            if rle_encode(row) == rle:
                logger.debug(f"possible interpretation: {row}")
                allowed.append(row)

        assert n_allowed == len(allowed)

        all_n_allowed.append(n_allowed)

    print(f"Sum of possible arrangement counts is {sum(all_n_allowed)}")
