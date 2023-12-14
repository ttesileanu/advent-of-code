#! /usr/bin/env python
from utils import iterinput, logger
from common7 import Hand, joker_mode


if __name__ == "__main__":
    joker_mode()

    value_hands = []
    for line in iterinput():
        logger.debug(f"{line=}")
        items = [_ for _ in line.split(" ") if _]
        assert len(items) == 2

        cards, bid = items
        hand = Hand(cards)
        bid = int(bid)
        logger.debug(f"{hand} {bid=}")

        value_hands.append((hand, bid))

    ranked_hands = sorted(value_hands, key=lambda _: _[0])
    logger.debug(f"{ranked_hands=}")

    earnings = 0
    for i, ranked_hand in enumerate(ranked_hands):
        earnings += (i + 1) * ranked_hand[1]

    print(f"Total earnings: {earnings}")
