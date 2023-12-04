#! /usr/bin/env python
import os

beats = {"A": "Y", "B": "Z", "C": "X"}
draws = {"A": "X", "B": "Y", "C": "Z"}
value = {"X": 1, "Y": 2, "Z": 3}

with open("input2.txt", "rt") as f:
    total = 0
    count = 0
    for line in f:
        player1, player2, *_ = line.split(" ")
        player1 = player1.strip()
        player2 = player2.strip()

        assert player1 in "ABC"
        assert player2 in "XYZ"

        score = (
            6 if player2 in beats[player1] else (3 if player2 == draws[player1] else 0)
        ) + value[player2]
        total += score
        count += 1

print(f"Total score: {total} in {count} games.")
