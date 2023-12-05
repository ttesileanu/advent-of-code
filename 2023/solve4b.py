#! /usr/bin/env python
import re
from utils import iterinput, logger


if __name__ == "__main__":
    regex = re.compile(r"Card \s*(\d+): ([\d\s]+) \| ([\d\s]+)")
    card_matches = []
    for i, line in enumerate(iterinput()):
        logger.debug(line)
        match = regex.fullmatch(line)
        assert match is not None

        card_id = int(match[1])
        # the algorithm below assumes that the card ID is just the (1-based) index
        assert card_id == i + 1

        left = [int(_) for _ in match[2].strip().split(" ") if _]
        right = [int(_) for _ in match[3].strip().split(" ") if _]

        logger.debug(f"{card_id=}: {left=} {right=}")

        matching = len(set(left).intersection(right))
        card_matches.append(matching)

        logger.debug(f"{card_id=} has {matching} matching cards")

    n = len(card_matches)
    repetitions = n * [1]

    for i, matching in enumerate(card_matches):
        logger.debug(f"card {i + 1} appears {matching} times")
        for k in range(i + 1, i + matching + 1):
            if k < n:
                repetitions[k] += repetitions[i]
            else:
                break

    print(f"Total number of cards: {sum(repetitions)}")
