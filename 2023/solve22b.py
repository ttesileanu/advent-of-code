#! /usr/bin/env python
from collections import defaultdict, deque
from utils import iterinput, logger

from common22 import drop_and_count_deps, load_blocks


if __name__ == "__main__":
    # The key observation here is that we can reuse the sizes of the chain reaction from
    # disintegrating higher bricks to calculate the size of the chain reaction from
    # lower bricks.

    # Suppose disintegrating brick x (y) leads to chain reaction X (Y), which is a set
    # of bricks that fall. Suppose there is a common brick a ∈ X, a ∈ Y. For it to be
    # disintegrates, all of its supports must have disintegrate in both X and Y.
    # Recursively, all *their* supports must have disintegrated, etc. As we follow this
    # chain, we go lower and lower, until eventually we end up on the level containing
    # either (the bottom of) brick x or that of y, whichever is higher. Now, the chain
    # X (Y) can't contain any bricks below the level of x (y), and on that level it can
    # only contain x (y), since effects can't propagate to the same level or below it.
    # We reach a contradiction if x and y are on the same level.

    # Our arguments above mean that (assuming x ≠ y):
    #   1. If x and y are on the same level, the chains X and Y must be disjoint.
    #   2. If x is lower than y and their chains X and Y are not disjoint, Y ⊂ X.
    #   3. If y is lower than x and their chains X and Y are not disjoint, X ⊂ Y.

    # This suggests a solution:
    #   * for each brick, we want to record both the reaction chain X and all the bricks
    #     outside of it that are affected by it, a dict
    #       Xbar = {b: number of supports of brick b that disappear due to X}
    #       (support here is a brick, not a single contact)
    #   * sort the bricks by minimum z level
    #   * for the highest brick x,
    #       X = {x}
    #       Xbar = {}
    #   * for each subsequent brick y, the reaction chain is the union of the reaction
    #     chains of all the dependent bricks that have no other dependents, plus the
    #     set of bricks that fall due to synergistic effects (e.g., several dependents
    #     contain the bricks in their Xbar)
    #       - the number of bricks that would fall is the sum of the numbers of bricks
    #         that would fall from the dependents, plus the number of bricks that would
    #         fall from synergistic effects

    blocks = load_blocks(iterinput())
    dep_results = drop_and_count_deps(blocks)
    supported_by = dep_results.supported_by
    supports = dep_results.supports
    logger.debug(f"{supports=}")

    chain_sizes = {}
    Xbar = {}

    # blocks were already sorted by `drop_and_count_deps`
    for i in range(len(blocks) - 1, -1, -1):
        deps = supports.get(i, [])
        if len(deps) == 0:
            chain_sizes[i] = 1
            Xbar[i] = {}
        else:
            # focus only on dependencies that would fall if we removed i
            falling_deps = [dep for dep in deps if len(supported_by[dep]) == 1]
            chain_sizes[i] = 1 + sum(chain_sizes[dep] for dep in falling_deps)

            # now what do we get from synergy?
            q = deque()
            for dep in falling_deps:
                q.extend(Xbar[dep].items())

            for dep in deps.difference(falling_deps):
                q.append((dep, 1))

            new_Xbar = defaultdict(int)
            while q:
                b, c = q.popleft()
                new_Xbar[b] += c
                assert new_Xbar[b] <= len(supported_by[b])
                if new_Xbar[b] == len(supported_by[b]):
                    # this brick falls
                    chain_sizes[i] += 1
                    new_Xbar.pop(b)
                    for bb in supports[b]:
                        q.append((bb, 1))

            Xbar[i] = new_Xbar

    logger.debug(f"{chain_sizes=}")
    assert len(chain_sizes) == len(blocks)

    count = sum(chain_sizes.values()) - len(blocks)
    print(f"The sum of the number of bricks that would fall is {count}")
