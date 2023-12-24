#! /usr/bin/env python
import math
from dataclasses import dataclass
from typing import Tuple, Union

from common8 import check_degrees, Multigraph
from utils import iterinput, logger

START_ENDING = "A"
TARGET_ENDING = "Z"


def check_no_leaves(graph: Multigraph):
    all_nodes = set(graph.children_map)
    for children in graph.children_map.values():
        for child in children:
            assert child in all_nodes


def extended_gcd(a: int, b: int, /) -> Tuple[int, int, int]:
    """Find GCD and Bézout coefficients.

    From https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm#Pseudocode.

    Parameters
    ----------
    a, b : int
        Integers for which to find the GCD.

    Returns
    -------
    gcd : int
        The GCD between `a` and `b`.
    x, y : int
        The Bézout coefficients, obeying `a * x + b * y = gcd`.
    """
    s = 0
    r = b

    old_s = 1
    old_r = a

    while r != 0:
        q = old_r // r

        old_s, s = s, old_s - q * s
        old_r, r = r, old_r - q * r

    gcd = old_r
    x = old_s
    if b != 0:
        y = (old_r - old_s * a) // b
    else:
        y = 0

    return gcd, x, y


@dataclass
class IntegerLattice:
    """An integer lattice, `base + k * step` for integer `k`.

    `base = None` stands for empty.
    """

    base: Union[int, None]
    step: Union[int, None]

    def intersect(self, other: "IntegerLattice") -> "IntegerLattice":
        """Return a new integer lattice that is the intersection of the two."""
        # The intersection is the lattice of integers n where
        #       n = base1 + step1 * k1 ,                                (1)
        #       n = base2 + step2 * k2 ,
        # for some integers k1 and k2.
        #
        # This implies
        #       base2 - base1 = step1 * k1 - step2 * k2 .              (2)
        # Bézout's identity implies that a solution exists iff
        #       base2 - base1 = delta = m * gcd(step1, step2) ,
        # where m is some integer.
        #
        # In that case, let x, y be Bézout coefficients, i.e.,
        #       gcd = step1 * x + step2 * y .
        # Then
        #       step1 * (x * m) - step2 * (-y * m) = m * gcd = base2 - base1 ,
        # which implies that a solution for equation (2) above is
        #       k1 = x * m ,  k2 = -y * m
        #
        # All pairs of solutions are given by
        #       (k1 + p * step2 / gcd, k2 + p * step1 / gcd)
        # where p is an integer.
        #
        # Plugging this into equation (1) above, we get that the integers n on the
        # intersection lattice obey
        #       n = base1 + x * m * step1 + p * step1 * step2 / gcd
        #         = base1 + x * m * step1 + p * lcm ,
        # where lcm is the least common multiplier, lcm = step1 * step2 / gcd.
        #
        # Similarly,
        #       n = base2 - y * m * step2 + p * step1 * step2 / gcd
        #         = base2 - y * m * step2 + p * lcm
        #         = base1 + (base2 - base1) - y * m * step2 + p * lcm
        #         = base1 + m * (gcd - y * step2) + p * lcm
        #         = base1 + m * x * step1 + p * lcm ,
        # where we used Bézout's identity. This matches the above.

        # In other words, the new lattice is given by
        #       base = base1 + x * m * step1
        #            = base1 + x * (base2 - base1) / gcd * step1
        #       step = lcm = step1 * step2 / gcd .

        if self.empty() or other.empty():
            return IntegerLattice(None, None)

        if self.step == 0 and other.step == 0:
            if self.base == other.base:
                return IntegerLattice(self.base, 0)
            else:
                return IntegerLattice(None, None)

        gcd, x, _ = extended_gcd(self.step, other.step)

        delta = other.base - self.base
        if delta % gcd != 0:
            return IntegerLattice(None, None)

        m = delta // gcd
        new_base = self.base + x * m * self.step
        new_step = self.step // gcd * other.step
        return IntegerLattice(new_base, new_step)

    def __and__(self, other: "IntegerLattice") -> "IntegerLattice":
        return self.intersect(other)

    def empty(self) -> bool:
        """Return true if this lattice is empty."""
        return self.base is None

    def first_after(self, start: int) -> Union[int, None]:
        """Find the smallest entry in the lattice that is larger than or equal to a
        starting point.

        Returns `None` if the lattice is empty or it contains a single element that is
        smaller than `start`.
        """
        # we have
        #       base + k * step >= start
        #   =>  k >= (start - base) / step
        # smallest integer larger than or equal to something is the ceil:
        #       k = ceil((start - base) / step) .

        if self.empty():
            return None
        if self.step == 0:
            if self.base >= start:
                return self.base
            else:
                return None

        # can't use floating point because of overflow
        # instead use:
        #       ceil(n / m) = floor((n - 1) / m) + 1
        # (https://en.wikipedia.org/wiki/Floor_and_ceiling_functions)
        k = (start - self.base - 1) // self.step + 1
        return self.base + k * self.step

    def __repr__(self) -> str:
        if self.empty():
            return "<EMPTY>"
        else:
            return f"<{self.base} + k * {self.step}>"


if __name__ == "__main__":
    it = iterinput()
    instructions = next(it)
    logger.debug(f"Instructions: {instructions}")

    graph = Multigraph.from_iterator(it)
    logger.debug(f"{graph!r}")
    logger.debug(f"Number of nodes in graph: {len(graph.children_map)}")
    check_degrees(graph)
    check_no_leaves(graph)

    nodes = [node for node in graph.children_map if node.endswith(START_ENDING)]
    assert len(nodes) == len(
        [node for node in graph.children_map if node.endswith(TARGET_ENDING)]
    )
    logger.debug(f"Number of initial nodes: {len(nodes)}")

    # Given a node S_i and a position l in the instruction set, the next node is fully
    # determined by the graph. Let N be the number of nodes in the graph and L be the
    # length of the instruction set. The number of possible (S_i, l) pairs is at most
    # N * L, so the sequence of pairs starting at (S_i, 0) must loop eventually --
    # though note that S_i itself might not ever be reached again.
    #
    # Suppose ending nodes are encountered on the path starting at (S_i, 0) only after
    # the looping sequence starts. Suppose they occur at positions k'_{ij}. Let us focus
    # on only one of these ending nodes, and call its position k_i.

    # The termination criterion is satisfied when ending nodes are encountered along all
    # paths:
    #       k_1 + a_1 * T_1 = k_2 + a_2 * T_2 = ... = k_M + a_M * T_M ,
    # where M is the number of starting nodes.

    # Each of these equations models an integer lattice, so the final solution involves
    # intersecting these lattices. Note that intersecting two lattices gives another
    # lattice (or any empty set).

    # Note that if there were any ending nodes during the "warmup" periods (before the
    # loops) we would need some extra processing. It would be sufficient to simply run
    # the simulation on all chains forward until the maximum warmup period to see if we
    # run into a match across all chains.

    # Similarly, if each loop contains more than one ending node, we need to check all
    # possible combinations of matches (i.e., set each k_i to each possible choice of
    # k'_{ij}) to search for the earliest coincidence. This could easily get out of
    # hand, of course.

    # Here we implement the latter contingency but not the former. This is because the
    # latter occurs in one of the examples while the former does not.

    n = len(instructions)
    loops = []
    loop_starts = []
    loop_lengths = []
    loop_ending_idxs = []

    for starting_node in nodes:
        logger.debug(f"Finding loop starting with {starting_node}")
        node = starting_node
        count = 0
        loop = []
        loop_start = None
        visited = set()
        while True:
            ip = count % n
            entry = (node, ip)
            if entry in visited:
                loop_start = loop.index(entry)
                break
            else:
                loop.append(entry)
                visited.add(entry)

            instruction = instructions[ip]
            # logger.debug(f"{node=}, {ip=}, {instruction=}")
            if instruction == "L":
                # logger.debug(f"going left...")
                node = graph.get_left_child(node)
            elif instruction == "R":
                # logger.debug(f"going right...")
                node = graph.get_right_child(node)
            else:
                raise ValueError(f"Unknown instruction {instruction}")

            count += 1

        assert len(set(loop)) == len(loop)

        loop_length = len(loop) - loop_start

        loops.append(loop)
        loop_starts.append(loop_start)
        loop_lengths.append(loop_length)

        logger.debug(
            f"    Chain starting with {loop[0][0]} starts "
            f"loop at {loop_start} with period {loop_length}"
        )

        ending_warmup = [_ for _ in loop[:loop_start] if _[0].endswith(TARGET_ENDING)]
        ending_loop = [_ for _ in loop[loop_start:] if _[0].endswith(TARGET_ENDING)]
        n_ending_warmup = len(ending_warmup)
        n_ending_warmup_unique = len(set(ending_warmup))
        n_ending_loop = len(ending_loop)
        n_ending_loop_unique = len(set(ending_loop))

        ending_idxs = [i for i, _ in enumerate(loop) if _[0].endswith(TARGET_ENDING)]
        loop_ending_idxs.append(ending_idxs)

        # logger.debug(f"{loop=}")
        logger.debug(f"        {n_ending_warmup=}, {n_ending_warmup_unique=}")
        logger.debug(f"        {n_ending_loop=}, {n_ending_loop_unique=}")
        logger.debug(f"        ending nodes at {ending_idxs}")

        assert n_ending_warmup == 0
        assert n_ending_loop >= 1

    lattices = [IntegerLattice(0, 1)]
    for ending_idxs, loop_length in zip(loop_ending_idxs, loop_lengths):
        new_lattices = []
        for ending_idx in ending_idxs:
            other_lattice = IntegerLattice(ending_idx, loop_length)
            for lattice in lattices:
                logger.debug(f"lattice={lattice!s}, other_lattice={other_lattice!s}")

                new_lattice = lattice & other_lattice
                if not new_lattice.empty():
                    new_lattices.append(new_lattice)

        lattices = new_lattices
        assert len(lattices) > 0

    logger.debug(f"Lattices of solutions: {lattices}")
    warmup = max(loop_starts)
    count = min(lattice.first_after(warmup) for lattice in lattices)
    print(f"Number of steps to reach nodes ending in {TARGET_ENDING}: {count}")
