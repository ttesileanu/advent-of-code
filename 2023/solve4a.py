#! /usr/bin/env python
import re
from utils import iterinput, logger


if __name__ == "__main__":
    regex = re.compile(r"Card \s*(\d+): ([\d\s]+) \| ([\d\s]+)")
    winnings = 0
    for line in iterinput():
        logger.debug(line)
        match = regex.fullmatch(line)
        assert match is not None

        card_id = int(match[1])
        winners = [int(_) for _ in match[2].strip().split(" ") if _]
        haves = [int(_) for _ in match[3].strip().split(" ") if _]

        logger.debug(f"{card_id=}: {winners=} {haves=}")

        have_winners = set(winners).intersection(haves)
        if len(have_winners) > 0:
            game_winnings = 2 ** (len(have_winners) - 1)
        else:
            game_winnings = 0

        logger.debug(f"{card_id=} wins {game_winnings} points")

        winnings += game_winnings

    print(f"Total winnings: {winnings}")
