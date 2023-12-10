#! /usr/bin/env python
from utils import logger
from common6 import get_ways_to_win, read_input


if __name__ == "__main__":
    races = read_input()

    ways_to_win = []
    for race in races:
        logger.debug(f"{race=}")
        ways_to_win.append(get_ways_to_win(*race))

    product = 1
    for n in ways_to_win:
        product *= n

    print(f"Product of ways to win per race: {product}")
