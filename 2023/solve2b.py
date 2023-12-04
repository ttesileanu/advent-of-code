#! /usr/bin/env python
import re
from utils import iterinput, logger

if __name__ == "__main__":
    power_sum = 0

    game_regex = re.compile(r"Game (\d+)")
    color_regex = re.compile(r"(\d+) (red|blue|green)")
    for line in iterinput():
        logger.debug(f"processing line '{line.strip()}'")
        prefix, config_str = line.split(":")
        configs = [_.strip() for _ in config_str.split(";")]

        game_match = game_regex.fullmatch(prefix)
        assert game_match is not None

        game_id = int(game_match[1])

        possible = True
        max_counts = {"red": 0, "green": 0, "blue": 0}
        for config in configs:
            color_specs = [_.strip() for _ in config.split(",")]
            seen = set()
            for spec in color_specs:
                match = color_regex.fullmatch(spec)
                count = int(match[1])
                color = match[2]
                assert not color in seen

                max_counts[color] = max(max_counts[color], count)
                seen.add(color)

        logger.debug(f"{game_id=} balls needed: {max_counts}")

        power = 1
        for count in max_counts.values():
            power *= count

        logger.debug(f"{game_id=} {power=}")
        power_sum += power

    print(f"Sum of game powers is {power_sum}.")
