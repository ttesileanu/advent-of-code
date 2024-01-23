#! /usr/bin/env python
from common8 import check_degrees, Multigraph
from utils import IntegerLattice, iterinput, logger

START_ENDING = "A"
TARGET_ENDING = "Z"


def check_no_leaves(graph: Multigraph):
    all_nodes = set(graph.children_map)
    for children in graph.children_map.values():
        for child in children:
            assert child in all_nodes


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
