#! /usr/bin/env python
from collections import defaultdict
from enum import IntEnum
from functools import total_ordering
from typing import List, Sequence, Union

from utils import iterinput, logger


@total_ordering
class Card:
    SORTED = "23456789TJQKA"
    TO_VALUE = {ch: i for i, ch in enumerate(SORTED)}

    def __init__(self, card: str):
        assert len(card) == 1
        assert card in Card.SORTED

        self.value = Card.TO_VALUE[card]

    def __lt__(self, other: Union[str, "Card"]):
        if not isinstance(other, Card):
            other = Card(other)
        return self.value < other.value

    def __eq__(self, other: Union[str, "Card"]):
        if not isinstance(other, Card):
            other = Card(other)
        return self.value == other.value

    def __repr__(self) -> str:
        return f"[{Card.SORTED[self.value]}]"

    def __str__(self) -> str:
        return Card.SORTED[self.value]


class Hand:
    cards: List[str]

    class Type(IntEnum):
        HIGH_CARD = 0
        ONE_PAIR = 1
        TWO_PAIR = 2
        THREE_OF_A_KIND = 3
        FULL_HOUSE = 4
        FOUR_OF_A_KIND = 5
        FIVE_OF_A_KIND = 6

    def __init__(self, cards: Union[str, Sequence[str]]):
        assert len(cards) == 5
        self.cards = [Card(_) for _ in cards]

        self.type_ = self.calculate_type(self.cards)

    def __repr__(self) -> str:
        return f"Hand({self.cards}, {self.type_!s})"

    @staticmethod
    def calculate_type(cards: Sequence[str]) -> Type:
        counts = defaultdict(lambda: 0)
        for card in cards:
            counts[str(card)] += 1

        logger.debug(f"Card count: {counts=}")
        assert sum(counts.values()) == 5
        if len(counts) == 1:
            assert next(iter(counts.values())) == 5
            return Hand.Type.FIVE_OF_A_KIND
        elif len(counts) == 2:
            if 4 in counts.values():
                return Hand.Type.FOUR_OF_A_KIND
            else:
                assert 3 in counts.values()
                return Hand.Type.FULL_HOUSE
        elif len(counts) == 3:
            if 3 in counts.values():
                assert 2 not in counts.values()
                return Hand.Type.THREE_OF_A_KIND
            else:
                assert sorted(counts.values()) == [1, 2, 2]
                return Hand.Type.TWO_PAIR
        elif len(counts) == 4:
            assert sorted(counts.values()) == [1, 1, 1, 2]
            return Hand.Type.ONE_PAIR
        elif len(counts) == 5:
            assert all(_ == 1 for _ in counts.values())
            return Hand.Type.HIGH_CARD
        else:
            raise RuntimeError("More than 5 cards in the hand?!")

    def __lt__(self, other) -> bool:
        if self.type_ < other.type_:
            return True
        elif self.type_ > other.type_:
            return False
        else:
            for card1, card2 in zip(self.cards, other.cards):
                if card1 < card2:
                    return True
                elif card1 > card2:
                    return False

            return False


if __name__ == "__main__":
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
