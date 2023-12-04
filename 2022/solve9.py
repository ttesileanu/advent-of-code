#! /usr/bin/env python
from typing import List

with open("input9.txt", "rt") as f:
    head = [0, 0]
    tail = [0, 0]

    tail_locations = set()
    tail_locations.add(tuple(tail))
    for line in f:    
        line = line.strip()
        if len(line) == 0:
            continue

        direction, count_str, *_ = line.split(" ")
        assert len(_) == 0
        assert direction in "LRUD"

        count = int(count_str)
        assert count > 0

        if direction == "L":
            if head[1] >= tail[1]:
                # head is to the right of tail
                # first move left (tail doesn't need to move), then continue, if needed
                delta = min(count, 2 if head[1] > tail[1] else 1)
                head[1] -= delta
                count -= delta

            if count > 0:
                head[1] -= count
                tail[0] = head[0]
                for i in range(count):
                    tail[1] -= 1
                    tail_locations.add(tuple(tail))
        elif direction == "R":
            if head[1] <= tail[1]:
                # head is to the left of tail
                # first move right (tail doesn't need to move), then continue, if needed
                delta = min(count, 2 if head[1] < tail[1] else 1)
                head[1] += delta
                count -= delta

            if count > 0:
                head[1] += count
                tail[0] = head[0]
                for i in range(count):
                    tail[1] += 1
                    tail_locations.add(tuple(tail))
        elif direction == "D":
            if head[0] <= tail[0]:
                # head is above tail
                # first move down (tail doesn't need to move), then continue, if needed
                delta = min(count, 2 if head[0] < tail[0] else 1)
                head[0] += delta
                count -= delta

            if count > 0:
                head[0] += count
                tail[1] = head[1]
                for i in range(count):
                    tail[0] += 1
                    tail_locations.add(tuple(tail))
        else:  # direction == "U"
            if head[0] >= tail[0]:
                # head is below tail
                # first move up (tail doesn't need to move), then continue, if needed
                delta = min(count, 2 if head[0] > tail[0] else 1)
                head[0] -= delta
                count -= delta

            if count > 0:
                head[0] -= count
                tail[1] = head[1]
                for i in range(count):
                    tail[0] -= 1
                    tail_locations.add(tuple(tail))

        # print(f"after {line}, head at {head}, tail at {tail}")

print(f"the tail visited {len(tail_locations)} positions")
