from collections import defaultdict
from enum import IntEnum
from functools import total_ordering
from typing import List, Sequence, Union

from utils import logger


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
    JOKER_MODE = False

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

        type_ = None
        if len(counts) == 1:
            assert next(iter(counts.values())) == 5
            type_ = Hand.Type.FIVE_OF_A_KIND
        elif len(counts) == 2:
            if 4 in counts.values():
                type_ = Hand.Type.FOUR_OF_A_KIND
            else:
                assert 3 in counts.values()
                type_ = Hand.Type.FULL_HOUSE
        elif len(counts) == 3:
            if 3 in counts.values():
                assert 2 not in counts.values()
                type_ = Hand.Type.THREE_OF_A_KIND
            else:
                assert sorted(counts.values()) == [1, 2, 2]
                type_ = Hand.Type.TWO_PAIR
        elif len(counts) == 4:
            assert sorted(counts.values()) == [1, 1, 1, 2]
            type_ = Hand.Type.ONE_PAIR
        elif len(counts) == 5:
            assert all(_ == 1 for _ in counts.values())
            type_ = Hand.Type.HIGH_CARD
        else:
            raise RuntimeError("More than 5 cards in the hand?!")

        if Hand.JOKER_MODE and "J" in counts:
            if type_ == Hand.Type.HIGH_CARD:
                # turn J into random other
                type_ = Hand.Type.ONE_PAIR
            elif type_ == Hand.Type.ONE_PAIR:
                # turn 1x or 2x J into random other
                type_ = Hand.Type.THREE_OF_A_KIND
            elif type_ == Hand.Type.THREE_OF_A_KIND:
                # turn 1x J or 3x J into random other
                type_ = Hand.Type.FOUR_OF_A_KIND
            elif type_ == Hand.Type.FULL_HOUSE:
                # turn 2x J or 3x J into other
                type_ = Hand.Type.FIVE_OF_A_KIND
            elif type_ == Hand.Type.FOUR_OF_A_KIND:
                # turn 1x J or 4x J into other
                type_ = Hand.Type.FIVE_OF_A_KIND
            elif type_ == Hand.Type.TWO_PAIR:
                if counts["J"] == 1:
                    # turn 1x J into one of the pairs
                    type_ = Hand.Type.FULL_HOUSE
                else:
                    # turn both J into other
                    assert counts["J"] == 2
                    type_ = Hand.Type.FOUR_OF_A_KIND
            else:
                # nothing to do, already best card
                assert type_ == Hand.Type.FIVE_OF_A_KIND

        return type_

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


def joker_mode():
    Card.SORTED = "J23456789TQKA"
    Card.TO_VALUE = {ch: i for i, ch in enumerate(Card.SORTED)}
    Hand.JOKER_MODE = True
