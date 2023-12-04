#! /usr/bin/env python
import os

with open("input1.txt", "rt") as f:
    crt_sum = 0
    crt_max = 0
    for line in f:
        line = line.strip()
        if len(line) > 0:
            crt_sum += int(line)
        else:
            crt_max = max(crt_max, crt_sum)
            crt_sum = 0

    crt_max = max(crt_max, crt_sum)

print(f"Maximum-calorie elf carries {crt_max} calories.")

