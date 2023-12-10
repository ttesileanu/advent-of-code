#! /usr/bin/env python
from utils import logger
from common6 import get_ways_to_win, read_input


if __name__ == "__main__":
    races = read_input(ignore_spaces=True)
    assert len(races) == 1

    ways_to_win = get_ways_to_win(*races[0])

    print(f"Ways to win in big race: {ways_to_win}")
