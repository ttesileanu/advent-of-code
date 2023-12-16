#! /usr/bin/env python
from common8 import check_degrees, Multigraph
from utils import iterinput, logger

START = "AAA"
TARGET = "ZZZ"


if __name__ == "__main__":
    it = iterinput()
    instructions = next(it)
    logger.debug(f"Instructions: {instructions}")

    graph = Multigraph.from_iterator(it)
    logger.debug(f"{graph!r}")
    check_degrees(graph)

    count = 0
    node = START
    n = len(instructions)
    while node != TARGET:
        instruction = instructions[count % n]
        logger.debug(f"{node=}, {instruction=}")
        if instruction == "L":
            logger.debug(f"going left...")
            node = graph.get_left_child(node)
        elif instruction == "R":
            logger.debug(f"going right...")
            node = graph.get_right_child(node)
        else:
            raise ValueError(f"Unknown instruction {instruction}")

        count += 1

    print(f"Number of steps to reach {TARGET}: {count}")
