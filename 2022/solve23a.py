#! /usr/bin/env python
import sys
import math
from collections import defaultdict
from typing import List, Tuple, Set, Dict


class Board:
    def __init__(self, initial: List[str]):
        self.elves = self._locate_elves(initial)
        self.movement_order = "NSWE"
        self.movement_idx = 0

    def step(self) -> bool:
        proposals = self.propose()
        moved = self.update(proposals)

        self.movement_idx += 1
        return moved

    def propose(self) -> Dict[Tuple[int, int], Tuple[int, int]]:
        proposals = {}
        for elf in self.elves:
            free = self.free_neighbors(elf)
            if all(free):
                # this elf does not move
                proposals[elf] = elf
                continue

            n, ne, e, se, s, sw, w, nw = free
            for i in range(4):
                idx = (self.movement_idx + i) % 4
                direction = self.movement_order[idx]

                if direction == "N" and n and ne and nw:
                    proposals[elf] = (elf[0] - 1, elf[1])
                    break
                elif direction == "S" and s and se and sw:
                    proposals[elf] = (elf[0] + 1, elf[1])
                    break
                elif direction == "W" and w and nw and sw:
                    proposals[elf] = (elf[0], elf[1] - 1)
                    break
                elif direction == "E" and e and ne and se:
                    proposals[elf] = (elf[0], elf[1] + 1)
                    break

        return proposals

    def free_neighbors(
        self, pos: Tuple[int, int]
    ) -> Tuple[bool, bool, bool, bool, bool, bool, bool, bool]:
        row, col = pos
        elves = self.elves
        n = not ((row - 1, col) in elves)
        ne = not ((row - 1, col + 1) in elves)
        e = not ((row, col + 1) in elves)
        se = not ((row + 1, col + 1) in elves)
        s = not ((row + 1, col) in elves)
        sw = not ((row + 1, col - 1) in elves)
        w = not ((row, col - 1) in elves)
        nw = not ((row - 1, col - 1) in elves)
        return n, ne, e, se, s, sw, w, nw

    def update(self, proposals: Dict[Tuple[int, int], Tuple[int, int]]) -> bool:
        moved = False

        # dismiss proposals that yield collisions
        seen = set()
        to_dismiss = set()
        for target in proposals.values():
            if target in seen:
                to_dismiss.add(target)
            else:
                seen.add(target)

        # move the elves
        new_elves = set()
        for origin in self.elves:
            target = proposals.get(origin, origin)
            if target != origin and target not in to_dismiss:
                new_elves.add(target)
                moved = True
            else:
                new_elves.add(origin)

        self.elves = new_elves
        return moved

    @staticmethod
    def _locate_elves(l: List[str]) -> Set[Tuple[int, int]]:
        height = len(l)
        width = len(l[0])

        elves = set()
        for i in range(height):
            for j in range(width):
                ch = l[i][j]
                assert ch in "#."

                if ch == "#":
                    elves.add((i, j))

        return elves

    def get_range(self) -> Tuple[int, int, int, int]:
        """Return bounds for where elves are found, in the order
        (min_row, max_row, min_col, max_col)
        (all inclusive)
        """
        min_row = math.inf
        max_row = -math.inf
        min_col = math.inf
        max_col = -math.inf
        for elf in self.elves:
            min_row = min(min_row, elf[0])
            max_row = max(max_row, elf[0])
            min_col = min(min_col, elf[1])
            max_col = max(max_col, elf[1])

        return (min_row, max_row, min_col, max_col)

    def empty_tiles(self) -> int:
        min_row, max_row, min_col, max_col = self.get_range()
        n_rows = max_row - min_row + 1
        n_cols = max_col - min_col + 1

        all_tiles = n_rows * n_cols
        return all_tiles - len(self.elves)

    def show(self):
        min_row, max_row, min_col, max_col = self.get_range()

        n_rows = max_row - min_row + 1
        n_cols = max_col - min_col + 1

        board = [n_cols * ["."] for _ in range(n_rows)]

        for elf in self.elves:
            board[elf[0] - min_row][elf[1] - min_col] = "#"

        for row in board:
            print("".join(row))


fname = "input23" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    # add some padding to the board
    initial = []
    width = None
    for line in f:
        line = line.strip()
        if len(line) == 0:
            # map ended
            break

        initial.append(line)
        if width == None:
            width = len(line)
        else:
            assert len(line) == width

board = Board(initial)
board.show()

print("---")

i = 0
moved = True
while moved:
    i += 1
    moved = board.step()

board.show()

print(f"first round where elves don't move: {i}")
