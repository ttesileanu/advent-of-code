#! /usr/bin/env python
from common8 import check_degrees, Multigraph
from utils import iterinput, logger

START_ENDING = "A"
TARGET_ENDING = "Z"


if __name__ == "__main__":
    it = iterinput()
    instructions = next(it)
    logger.debug(f"Instructions: {instructions}")

    graph = Multigraph.from_iterator(it)
    logger.debug(f"{graph!r}")
    logger.debug(f"Number of nodes in graph: {len(graph.children_map)}")
    check_degrees(graph)

    nodes = [node for node in graph.children_map if node.endswith(START_ENDING)]
    assert len(nodes) == len(
        [node for node in graph.children_map if node.endswith(TARGET_ENDING)]
    )
    logger.debug(f"Number of initial nodes: {len(nodes)}")

    count = 0
    n = len(instructions)
    while not all(node.endswith(TARGET_ENDING) for node in nodes):
        instruction = instructions[count % n]
        logger.debug(f"{nodes=}, {instruction=}")
        if instruction == "L":
            logger.debug(f"going left...")
            new_nodes = []
            for node in nodes:
                new_nodes.append(graph.get_left_child(node))
        elif instruction == "R":
            logger.debug(f"going right...")
            new_nodes = []
            for node in nodes:
                new_nodes.append(graph.get_right_child(node))
        else:
            raise ValueError(f"Unknown instruction {instruction}")

        nodes = new_nodes

        count += 1

    print(f"Number of steps to reach nodes ending in {TARGET_ENDING}: {count}")
