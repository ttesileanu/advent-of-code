#! /usr/bin/env python

import enum
from typing import Union, Literal, Sequence


class Bound(float, enum.Enum):
    Inf = float("inf")
    NegInf = float("-inf")


DIGITS = [str(_) for _ in range(1, 10)]
TEXTS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def sfind(s: str, pattern: str) -> Union[int, Literal[Bound.Inf]]:
    idx = s.find(pattern)
    return idx if idx >= 0 else Bound.Inf


def sfind_back(s: str, pattern: str) -> Union[int, Literal[Bound.NegInf]]:
    idx_back = s[::-1].find(pattern[::-1])
    if idx_back == -1:
        return Bound.NegInf

    return len(s) - len(pattern) - idx_back


def argmin(l: Sequence[Union[int, float]]):
    return min(range(len(l)), key=l.__getitem__)


def find_first(s: str) -> str:
    idx_digit = [sfind(s, digit) for digit in DIGITS]
    idx_text = [sfind(s, text) for text in TEXTS]

    first_digit = min(idx_digit)
    first_text = min(idx_text)

    if first_digit < first_text:
        return s[first_digit]
    else:
        which = DIGITS[idx_text.index(first_text)]
        return which


def find_last(s: str) -> str:
    idx_digit = [sfind_back(s, digit) for digit in DIGITS]
    idx_text = [sfind_back(s, text) for text in TEXTS]

    last_digit = max(idx_digit)
    last_text = max(idx_text)

    if last_digit > last_text:
        return s[last_digit]
    else:
        which = DIGITS[idx_text.index(last_text)]
        return which


with open("input1.txt", "rt") as f:
    calibrations = []

    for line in f:
        digit1 = find_first(line)
        digit2 = find_last(line)
        calibration = int(digit1 + digit2)
        calibrations.append(calibration)

print(f"The sum of all calibration values is {sum(calibrations)}.")
