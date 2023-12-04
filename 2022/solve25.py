#! /usr/bin/env python
import sys


snafu_map = {"=": -2, "-": -1, "0": 0, "1": 1, "2": 2}
int_map = {0: "=", 1: "-", 2: "0", 3: "1", 4: "2"}


def from_snafu(s: str) -> int:
    factor = 1
    res = 0
    for i in range(len(s)):
        ch = s[len(s) - i - 1]
        res += factor * snafu_map[ch]

        factor *= 5

    return res


def to_snafu(x: int) -> str:
    l = []
    while x > 0:
        ch = int_map[(x + 2) % 5]
        l.append(ch)
        x = (x + 2) // 5

    s = "".join(l[::-1])
    return s


fname = "input25" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    numbers = []
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        numbers.append(from_snafu(line))

s = sum(numbers)
print(f"total fuel needed {s}, in SNAFU: {to_snafu(s)}")
