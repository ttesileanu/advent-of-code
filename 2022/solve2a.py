#! /usr/bin/env python
import os

beats = {"A": "B", "B": "C", "C": "A"}
loses = {"A": "C", "B": "A", "C": "B"}
value = {"A": 1, "B": 2, "C": 3}
scoremap = {"X": 0, "Y": 3, "Z": 6}

with open("input2.txt", "rt") as f:
    total = 0
    count = 0
    for line in f:
        player, result, *_ = line.split(" ")
        player = player.strip()
        result = result.strip()

        assert player in "ABC"
        assert result in "XYZ"

        if result == "X":
            me = loses[player]
        elif result == "Y":
            me = player
        else:  # result == "Z"
            me = beats[player]

        score = scoremap[result] + value[me]
        total += score
        count += 1

print(f"Total score: {total} in {count} games.")
