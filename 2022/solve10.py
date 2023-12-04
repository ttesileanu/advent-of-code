#! /usr/bin/env python

with open("input10.txt", "rt") as f:
    x = 1
    x_history = []
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        x_history.append(x)
        if line == "noop":
            continue

        assert line.startswith("addx ")
        x_history.append(x)
        value = int(line[5:])

        x += value

total_signal = 0
for i in range(19, len(x_history), 40):
    total_signal += (i + 1) * x_history[i]
    print(f"{i + 1}: {x_history[i]}")

print(f"total signal strength: {total_signal}")
# print(x_history)
