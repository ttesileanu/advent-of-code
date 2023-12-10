#! /usr/bin/env python
import math

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


if __name__ == "__main__":
    it = iterinput()

    times_str = next(it)
    assert times_str.startswith("Time:")
    times = [int(_) for _ in times_str[5:].split(" ") if _]

    records_str = next(it)
    assert records_str.startswith("Distance:")
    records = [int(_) for _ in records_str[9:].split(" ") if _]

    assert len(times) == len(records)
    races = list(zip(times, records))

    for line in it:
        assert not line.strip()

    logger.debug(f"{races=}")

    ways_to_win = []
    for race in races:
        logger.debug(f"{race=}")
        ways_to_win.append(get_ways_to_win(*race))

    product = 1
    for n in ways_to_win:
        product *= n

    print(f"Product of ways to win per race: {product}")
