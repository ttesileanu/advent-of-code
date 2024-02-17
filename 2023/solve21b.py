#! /usr/bin/env python
import time
from collections import deque
from typing import List, Tuple

from utils import loadmatrix, logger


START = "S"
GARDEN = "."
ROCK = "#"

# N_STEPS = 6
# N_STEPS = 64
N_STEPS = 26501365


def neighbors(x: Tuple[int, int]) -> List[Tuple[int, int]]:
    l = []
    l.append((x[0] - 1, x[1]))
    l.append((x[0] + 1, x[1]))
    l.append((x[0], x[1] - 1))
    l.append((x[0], x[1] + 1))
    return l


if __name__ == "__main__":
    # Got some inspiration from
    # https://www.reddit.com/r/adventofcode/comments/18nevo3/2023_day_21_solutions/?rdt=50708

    # The basic trick here is that the row and column going through the starting point
    # contain no rocks. This means that there is an obvious shortest path to get from
    # one tile to another. Specifically, the path to take is along the empty columns and
    # rows until we reach the closest "center" that's closest to the actual starting
    # point, then take the shortest path from there to the final location. "Center" here
    # means one of the duplicates of the starting point. To see that this works, simply
    # note that any path to the final location goes through the empty column and row
    # through the center mentioned above, and the shortest path to that point goes along
    # empty rows and columns.

    # Note: annoyingly, for the example input the row and column through the starting
    #       point are not empty. For both the example and the actual input, the spots
    #       on the perimeter of the tile contain no rocks, which may help, but we do not
    #       pursue that possibility here.

    # So why does this matter? Testing whether a certain spot is reachable from the
    # starting point in N steps is easy: it is reachable if and only if the shortest
    # path to that spot has length K such that K <= N, and K % 2 == N % 2. The shortest
    # path to any point on the infinite map can be expressed in terms of the shortest
    # path on a single tile.

    # We can turn this on its head and reason as follows. Let di, dj be row- and column-
    # distances from the starting point, and let -H <= di <= H and -W < dj < W (where
    # (H, W) is the shape of the map). Given the shortest distance from S to (di, dj),
    # we can calculate the shortest distance to any of the duplicates of (di, dj) that
    # appear in the infinitely many tiles of the map.

    # The key observation is that the shortest path to some position (i, j) that's not
    # in that central region always passes through some other center C that's near the
    # target position, provided that both the row and column of C are at least as close
    # to S as i and j. To see this, simply note that the shortest path to (i, j) must
    # pass through the (empty) row and column that go through C in order to reach the
    # target. Since there is a path from S to C that goes unobstructed along empty rows
    # and columns, the shortest path to (i, j) can contain that path. (This will not be
    # unique, but we don't need a unique path: its length is unique, and that's all we
    # need.)

    # For simplicity, we will further assume that W = H and H % 2 == 1, which is true
    # for our input. The general solution follows the same pattern but involves a lot
    # more bookkeeping, so we don't bother with it.

    # Back to counting: let us try to find out how many spots there are that are mirrors
    # of (di, dj) and are reachable in exactly N steps. In addition to (di, dj), such
    # spots are indexed by (ki, kj), the number of tiles we need to move in the row and
    # column directions. To avoid over-counting, ki, kj are constrained such that
    # sgn(ki) = sgn(di), sgn(kj) = sgn(dj), except when ki or kj are 0 (we use the
    # convention where sgn(0) = 1).

    # To put this differently, we split the region -H <= di, dj < H into four quadrants;
    # in counter-clockwise order:
    #   1.  0 <= di < H,    0 <= dj < H
    #   2.  0 <= di < H,   -H <= dj < 0
    #   3. -H <= di < 0,   -H <= dj < 0
    #   4. -H <= di < 0,    0 <= dj < H .
    # Each of these has generates mirrors according to the non-negative integers
    # ki, kj = 0, 1, ...:
    #   1. (di + H * ki, dj + H * kj)
    #   2. (di + H * ki, dj - H * kj)
    #   3. (di - H * ki, dj - H * kj)
    #   4. (di - H * ki, dj + H * kj) .
    # The shortest distance to one of these mirrors is easy to calculate: it is the
    # Manhattan distance from S to (±H * ki, ±H * kj), because you can go along empty
    # rows and columns between those points; plus the distance from (±H * ki, ±H * kj)
    # to the final target, which is the same as the distance from S to (di, dj). In
    # other words,
    #   d(di, dj, ki, kj) = H * (ki + kj) + d(di, dj, 0, 0) ,
    # where d is the distance from S to the point in the appropriate quadrant.

    # Let us call
    #   n(di, dj) = d(di, dj, 0, 0) .
    # We must find all ki, kj such that
    #   d(di, dj, ki, kj) <= N    and   d(di, dj, ki, kj) % 2 = N % 2 .
    # The latter condition becomes
    #   (H * (ki + kj)) % 2 = (N - n(di, dj)) % 2 ,
    # which is the same as
    #   (ki + kj) % 2 = N' % 2 ,
    # since we assumed that H is odd, and we used the notation
    #   N' = N - n(di, dj) .
    # (we're assuming N' > 0 below.)

    # We also must have
    #   H * (ki + kj) <= N' ,
    # so that
    #   ki + kj <= N' // H .
    # Let k = ki + kj. We have k <= N' // H and k % 2 = N' % 2, and for each k, we have
    # k + 1 possible positions ((0, k), (1, k - 1), ..., (k, 0)).

    # What is the sum of numbers from a to b in steps of 2? Let (b - a) // 2 = c. Then
    # the actual last number in the sum will be b' = a + 2 * c. The sum is
    #   S = a + (a + 2) + ... + (a + 2 * c) = (c + 1) * a + 2 * (1 + ... + c)
    #     = (c + 1) * a + c * (c + 1) = (c + 1) * (c + a) .

    # In our case, a = N' % 2 + 1, b = N' // H + 1.

    mat = loadmatrix()
    logger.debug(f"{mat=}")

    start = None
    for i, row in enumerate(mat.data):
        if row.count(START) > 0:
            assert start is None
            assert row.count(START) == 1
            start = (i, row.index(START))

    logger.info(f"Starting from {start}")
    mat[start[0], start[1]] = GARDEN

    # check that our assumptions are obeyed
    assert mat.nrows == mat.ncols
    H = mat.nrows
    for i in range(H):
        assert mat[i, start[1]] == GARDEN
        assert mat[start[0], i] == GARDEN

    t_cont = time.time()
    t0 = time.time()
    tile_dist = {start: 0}
    q = deque([start])
    visited = set([start])

    # XXX this is a hack, max_dist could be larger in principle
    max_dist = 4 * H

    while q:
        loc = q.popleft()
        d = tile_dist[loc]

        t1 = time.time()
        if t1 - t0 >= 5:
            dt = t1 - t_cont
            logger.info(
                f"{dt:.0f}s: distance {d} / {max_dist}, {len(visited)} visited, "
                f"len(q)={len(q)}"
            )
            t0 = t1

        if d >= max_dist:
            continue

        for neigh in neighbors(loc):
            if neigh not in visited:
                visited.add(neigh)

                i = neigh[0] % H
                j = neigh[1] % H
                if mat[i, j] == GARDEN:
                    tile_dist[neigh] = d + 1
                    q.append(neigh)

    count = 0
    for di in range(-H, H):
        for dj in range(-H, H):
            loc = (start[0] + di, start[1] + dj)
            if loc in tile_dist:
                d = tile_dist[loc]
                dprime = N_STEPS - d

                a = dprime % 2 + 1
                b = dprime // H + 1
                c = (b - a) // 2
                s = (c + 1) * (c + a)
                count += s

    print(f"The elf can reach {count} plots in {N_STEPS} steps")
