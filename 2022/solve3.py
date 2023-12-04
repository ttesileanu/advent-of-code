#! /usr/bin/env python
import os

def priority(ch: str) -> int:
    assert len(ch) == 1
    code = ord(ch) - ord("a") + 1
    if code < 0:
        code += 58

    return code

with open("input3.txt", "rt") as f:
    mistakes = []
    for line in f:
        items = line.strip()
        assert len(items) % 2 == 0

        mid = len(items) // 2
        items1 = items[:mid]
        items2 = items[mid:]

        common = set(items1) & set(items2)
        assert len(common) == 1

        mistakes.append(common.pop())

priorities = [priority(_) for _ in mistakes]
print(f"Sum of priorities of repeated item types: {sum(priorities)}")
