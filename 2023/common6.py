"""Common definitions for the two phases of day 6."""
import math
from typing import Sequence, Tuple

from utils import iterinput, logger


# the allowed strategies are of the form:
#     (assuming race duration is T ms)
# * spend a time v ms pressing the button, in which case the speed is v mm/ms
# * release and spend (T - v) ms racing...
# * ...leading to a distance traveled d = v * (T - v) mm
#
# if the current record is r mm, you will beat the record as long as
#       v * (T - v) > r
# <=>   v**2 - v * T + r < 0
# <=>   v is in-between the two roots


def get_ways_to_win(T: int, r: int) -> int:
    delta = T**2 - 4 * r

    if delta > 0:
        sqrt_delta = math.sqrt(delta)
        root_left = (T - sqrt_delta) / 2
        root_right = (T + sqrt_delta) / 2

        start = int(math.floor(root_left) + 1)
        stop = int(math.ceil(root_right) - 1)

        logger.debug(
            f"Beat record with v in [{start}, {stop}] "
            f"(approx of ({root_left}, {root_right}))"
        )

        return stop - start + 1
    elif delta <= 0:
        if delta == 0:
            logger.debug(f"Can only achieve record, can't beat it")
        else:
            logger.warning(f"All predicted distances < record, record is impossible!")
        return 0


def read_input(ignore_spaces: bool = False) -> Sequence[Tuple[int, int]]:
    it = iterinput()

    times_str = next(it)
    assert times_str.startswith("Time:")
    times_str = times_str[5:]

    if not ignore_spaces:
        times = [int(_) for _ in times_str.split(" ") if _]
    else:
        times = [int(times_str.replace(" ", ""))]

    records_str = next(it)
    assert records_str.startswith("Distance:")
    records_str = records_str[9:]

    if not ignore_spaces:
        records = [int(_) for _ in records_str.split(" ") if _]
    else:
        records = [int(records_str.replace(" ", ""))]

    assert len(times) == len(records)
    races = list(zip(times, records))

    for line in it:
        assert not line.strip()

    logger.debug(f"{races=}")

    return races
