#! /usr/bin/env python
import os

n_elves = 3
with open("input1.txt", "rt") as f:
    all_sums = []
    crt_sum = 0
    for line in f:
        line = line.strip()
        if len(line) > 0:
            crt_sum += int(line)
        else:
            all_sums.append(crt_sum)
            crt_sum = 0

    if crt_sum > 0:
        all_sums.append(crt_sum)

top_sums = sorted(all_sums)[-n_elves:]

print(f"Top three calorie-carrying elves carry: {top_sums} calories.")
print(f"Total: {sum(top_sums)} calories.")

