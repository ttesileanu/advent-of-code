#! /usr/bin/env python
from itertools import product
from typing import Iterator, List

from utils import iterinput, logger


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
    # Try a recursive approach works. Let
    #       M(r[0], ..., r[n-1]; p[0], ..., p[k-1])
    # be the number of arrangements that are consistent between the first representation
    # (modeled by r[i]) and the second representation (modeled by p[i]).
    #
    # r[i] \in {., #, ?}
    # p[i] \in {1, ...}
    #
    # * clearly all p[i] <= n; in fact, sum p[i] <= n - k + 1.

    # We have
    # * M(r[0:n], "."; p[0:k]) = M(r[0:n]; p[0:k])
    # * M(r[0:n], "#"; p[0:k])
    #       =  0 if k == 0
    #       =  0 if n == 0 and (k > 1 or p[k-1] != 1)
    #       =  1 if n == 0 and k == 1 and p[0] == 1         [LEFT WITH n > 0]
    #       =  0 if r[n-1] == "." and p[k-1] != 1
    #       =  M(r[0:n-1]; p[0:k-1])  if r[n-1] == "." and p[k-1] == 1
    #       =  0 if r[n-1] == "#" and p[k-1] < 2
    #       =  M(r[0:n]; p[0:k-1], p[k-1] - 1) if r[n-1] == "#" and p[k-1] >= 2
    #       =  M(r[0:n-1], ".#"; p[0:k]) + M(r[0:n-1], "##"; p[0:k]) if r[n-1] == "?"
    # * M(r[0:n], "?"; p[0:k])
    #       =  M(r[0:n], "."; p[0:k]) + M(r[0:n], "#"; p[0:k])
    # * M([]; p[0:k])
    #       =  0 if k > 0
    #       =  1 if k == 0

    # To make this efficient, note that we don't actually have to keep track of all the
    # values of M. Let
    #       R[0:N] and P[0:K]
    # be the actual sequences under consideration. We are ultimately interested in
    # calculating
    #       Count = M(R[0:N]; P[0:K]) .
    # Let us define
    #       M'(n, C, k, V) = M(R[0:n], C; P[0:k], V) ,
    # where C is a single character and V a single numeric value. That is, M' is the
    # number of arrangements that we get when we use a prefix of the actual sequences R
    # and K, with a single-character suffix added. The final value that we need is thus
    #       Count = M'(R[0:N-1], R[N-1]; P[0:K-1]; P[K]) .
    # (assuming here N > 0 and K > 0, which is always true in our dataset)

    # Can we rephrase the iteration in terms of M'?
    # (assuming V > 0, n > 0)
    # * M'(0, ".", k, V) = 0
    # * M'(0, "#", k, V) = 1 if k == 0 and V == 1 else 0
    # * M'(0, "?", k, V) = 1 if k == 0 and V == 1 else 0
    # * M'(n, "?", k, V) = M'(n, ".", k, V) + M'(n, "#", k, V)
    # * M'(n, ".", k, V) = M'(n-1, R[n-1], k, V)
    # * M'(n, "#", k, V)
    #       =  0                                if R[n-1] == "." and V != 1
    #       =  0                                if n == 1 and R[n-1] == "." and k > 0
    #       =  1                                if n == 1 and R[n-1] == "." and k == 0 and V == 1
    #       =  M'(n-2, R[n-2], k-1, P[K-1])     if R[n-1] == "." and V == 1
    #       =  0                                if R[n-1] == "#" and V < 2
    #       =  M'(n-1, R[n-1], k, V-1)          if R[n-1] == "#" and V >= 2
    #       =  M'(n, ".", k, V) + M'(n, "#", k, V)
    #                                           if R[n-1] == "?"
    # * M'(n, "?", k, V) = M'(n, ".", k, V) + M'(n, "#", k, V)

    # Let us define
    #       M''(n, C1, C2, k, V) = M(R[0:n], C1, C2; P[0:k], V)
    # (assuming V >= 0, n >= 0, k >= 0)
    # (V == 0 allowed to represent no added value in format 2)
    # * M''(0, "..", 0, V) = 1 if V == 0 else 0
    # * M''(0, ".#", 0, V) = 1 if V == 1 else 0
    # * M''(0, "#.", 0, V) = 1 if V == 1 else 0
    # * M''(0, "##", 0, V) = 1 if V == 2 else 0
    # * M''(0, "?.", 0, V) = 1 if V in [0, 1] else 0
    # * M''(0, "?#", 0, V) = 1 if V in [1, 2] else 0
    # * M''(n, C, "?", k, V) = M''(n, C, ".", k, V) + M''(n, C, "#", k, V)
    #
    # assuming n > 0:
    #
    # * M''(n, C, ".", k, V) = M''(n-1, R[n-1], C, k, V)
    # * M''(n, ".#", k, V)
    #       =  0                                        if V != 1
    #       =  M''(n-1, R[n-1], R[n-1], 0, 0)           if V == 1 and k == 0
    #       =  M''(n-1, R[n-1], ".", k-1, P[k-1])       if V == 1 and k > 0
    # * M''(n, "##", k, V)
    #       =  0                                        if V < 2
    #       =  M''(n-1, R[n-1], "#", k, V-1)            if V >= 2
    # * M''(n, "?#", k, V)
    #       =  M''(n, ".#", k, V) + M''(n, "##", k, V)

    n_allowed = []
    for line in iterinput():
        corrupted_row, rle_str = line.split(" ")
        rle = [int(_) for _ in rle_str.split(",")]

        logger.debug(f"{corrupted_row=}, {rle=}")

        allowed = []
        for row in possible_arrangements(corrupted_row):
            if rle_encode(row) == rle:
                logger.debug(f"possible interpretation: {row}")
                allowed.append(row)

        assert allowed
        n_allowed.append(len(allowed))

    print(f"Sum of possible arrangement counts is {sum(n_allowed)}")
