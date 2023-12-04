#! /usr/bin/env python
import os


def priority(ch: str) -> int:
    assert len(ch) == 1
    code = ord(ch) - ord("a") + 1
    if code < 0:
        code += 58

    return code


with open("input3.txt", "rt") as f:
    all_items = [_.strip() for _ in f.readlines()]

    assert len(all_items) % 3 == 0

    badges = []
    count = len(all_items) // 3
    for i in range(count):
        triplet = all_items[3 * i : 3 * (i + 1)]
        common = set(triplet[0]) & set(triplet[1]) & set(triplet[2])
        assert len(common) == 1

        badges.append(common.pop())

print(badges)

priorities = [priority(_) for _ in badges]
print(f"Sum of badge priorities: {sum(priorities)}")
