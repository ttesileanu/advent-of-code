#! /usr/bin/env python
import sys
import time
from tqdm import tqdm
from collections import deque

from typing import List, Optional


class Simulation:
    def __init__(self, jet: List[int], width: int = 7, start_x: int = 2, gap_y: int = 3):
        self.width = width
        self.start_x = start_x
        self.gap_y = gap_y
        
        self.bottom = 0
        self.pit = deque([(1 << self.width) - 1])
        self.rock_type = 0
        
        self.n_types = 5

        self.rock_widths = [4, 3, 3, 1, 2]
        self.rock_heights = [1, 3, 3, 4, 2]
        
        self.jet = jet
        self.jet_idx = 0
        
        self.rock_mapping = [
            self.horizontal, self.cross, self.ell, self.vertical, self.box
        ]
        self.rock_fct = None

        self.economy = True
        self.safety_margin = 45
        self.base = 0

    def throw_rock(self):
        self.rock_fct = self.rock_mapping[self.rock_type]
        rock_width = self.rock_widths[self.rock_type]
        rock_height = self.rock_heights[self.rock_type]

        width = self.width

        cx, cy = self.start_x, self.bottom + self.gap_y + 1 - self.base

        # make sure we have enough space in our pit
        to_add = cy + rock_height - len(self.pit)
        if to_add > 0:
            self.pit.extend(0 for _ in range(to_add))

        while True:
            # move horizontally
            old_cx = cx
            cx += self.jet[self.jet_idx]

            self.jet_idx = (self.jet_idx + 1) % len(self.jet)

            # keep within bounds
            if cx < 0:
                cx = old_cx
            elif cx + rock_width > width:
                cx = old_cx
            elif self.collision(cx, cy):
                # we hit something
                cx = old_cx

            # move vertically
            old_cy = cy
            cy -= 1

            assert cy >= 0

            # did we hit anything?
            if self.collision(cx, cy):
                # yes! our run is over
                cy = old_cy
                break

        self.place(cx, cy)
        self.bottom = max(self.bottom, cy + rock_height - 1 + self.base)
        self.rock_type = (self.rock_type + 1) % self.n_types

        if self.economy and len(self.pit) > self.safety_margin:
            # nothing can (hopefully?) fall below this barrier, so we can chop off the
            # pit a bit
            to_delete = len(self.pit) - self.safety_margin
            self.base += to_delete
            for i in range(to_delete):
                self.pit.popleft()

    def horizontal(self, x: int, y: int, action: str, count: int = 4) -> bool:
        mask = (1 << count) - 1
        shift = self.width - x - count
        mask <<= shift

        if action == "test":
            return (self.pit[y] & mask) != 0
        else:  #  action == "place"
            self.pit[y] |= mask

        return False

    def vertical(self, x: int, y: int, action: str, count: int = 4) -> bool:
        shift = self.width - x - 1
        mask = 1 << shift

        if action == "test":
            for j in range(y, y + count):
                if (self.pit[j] & mask) != 0:
                    # collision!
                    return True
        else:  # action == "place"
            for j in range(y, y + count):
                self.pit[j] |= mask

        return False

    def cross(self, x: int, y: int, action: str) -> bool:
        res = self.horizontal(x, y + 1, action, count=3)
        if not res:
            return self.vertical(x + 1, y, action, count=3)
        else:
            return True


    def ell(self, x: int, y: int, action: str) -> bool:
        res = self.horizontal(x, y, action, count=3)
        if not res:
            return self.vertical(x + 2, y, action, count=3)
        else:
            return True

    def box(self, x: int, y: int, action: str) -> bool:
        res = self.horizontal(x, y, action, count=2)
        if not res:
            return self.horizontal(x, y + 1, action, count=2)
        else:
            return True

    def collision(self, x: int, y: int) -> bool:
        return self.rock_fct(x, y, action="test")

    def place(self, x: int, y: int):
        self.rock_fct(x, y, action="place")

    def show(self):
        print()
        n = len(self.pit)
        for k in range(n):
            row = self.pit[n - k - 1]
            print("".join(row))


fname = "input17" + (sys.argv[1] if len(sys.argv) > 1 else "") + ".txt"
print(f"reading from {fname}...")
with open(fname, "rt") as f:
    lines = [__ for __ in (_.strip() for _ in f) if len(__) > 0]
    assert len(lines) == 1

    jet = [1 if _ == ">" else -1 for _ in lines[0]]

sim1 = Simulation(jet)
sim2 = Simulation(jet)

t0 = time.time()

n_rocks = 1_000_000_000_000
i = 0
period = None
start_idx = None
cycle_start = None
cycle_height = None
skipped = 0
while i < n_rocks:
    sim1.throw_rock()
    i += 1

    if start_idx is None:
        sim2.throw_rock()
        sim2.throw_rock()

        if sim1.rock_type == sim2.rock_type and sim1.jet_idx == sim2.jet_idx:
            if sim1.pit == sim2.pit:
                # we found a cycle!
                # x[i] = x[2 * i]  --> i = T
                start_idx = i
                print(f"found cycle (length at most {period})")

                cycle_start = sim1.bottom
    elif cycle_height is None:
        if sim1.rock_type == sim2.rock_type and sim1.jet_idx == sim2.jet_idx:
            if sim1.pit == sim2.pit:
                # the cycle repeated -- now we know the height and period
                period = i - start_idx
                cycle_height = sim1.bottom - cycle_start
                print(f"the cycle has period {period} and height {cycle_height}")
                
                n_periods = (n_rocks - i) // period
                i = i + period * n_periods
                skipped = n_periods * cycle_height

t1 = time.time()

print(f"simulating {n_rocks} rocks took {t1 - t0:.3g} seconds")

total_height = sim1.bottom + skipped
print(f"the tower is {sim1.bottom + skipped} units tall")
