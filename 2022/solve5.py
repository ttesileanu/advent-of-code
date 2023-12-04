#! /usr/bin/env python
import os
import re
from typing import Tuple


with open("input5.txt", "rt") as f:
    stacks = []
    state = "initial"
    move_parser = re.compile("^move (\d+) from (\d+) to (\d+)$")
    for line in f:
        line = line.strip("\r\n")
        if state == "initial":
            # still reading the initial state
            assert (len(line) + 1) % 4 == 0
            if len(stacks) == 0:
                # initialize the stacks
                stacks = [[] for _ in range((len(line) + 1) // 4)]
            else:
                assert len(line) == 4 * len(stacks) - 1

            if line.startswith("["):
                # one more row of crates
                for i in range(len(stacks)):
                    crate = line[4 * i : 4 * (i + 1)].strip()
                    if len(crate) > 0:
                        assert len(crate) == 3
                        assert crate[0] == "["
                        assert crate[2] == "]"
                        stacks[i].append(crate[1])
            else:
                # this should just be the indices
                expected = " ".join(f" {_ + 1} " for _ in range(len(stacks)))
                assert line == expected

                # ensure the stacks are organized with top crate last
                stacks = [_[::-1] for _ in stacks]
                
                state = "moves"
        elif state == "moves":
            # parse the moves
            line = line.strip()
            if len(line) == 0:
                continue

            params = move_parser.fullmatch(line)
            assert params is not None

            groups = params.groups()
            assert len(groups) == 3

            count, initial, final = [int(_) for _ in groups]

            # handle 1-based input!
            initial -= 1
            final -= 1

            # actually move `count` crates from `initial` to `final`
            assert len(stacks[initial]) >= count
            stacks[final].extend(stacks[initial][-1:-count - 1:-1])
            del stacks[initial][-count:]

print("".join(_[-1] for _ in stacks))
