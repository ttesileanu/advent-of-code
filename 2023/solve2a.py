#! /usr/bin/env python
import re
from utils import iterinput, logger

MAX_COUNTS = {"red": 12, "green": 13, "blue": 14}


if __name__ == "__main__":
    id_sum = 0

    game_regex = re.compile(r"Game (\d+)")
    color_regex = re.compile(r"(\d+) (red|blue|green)")
    for line in iterinput():
        logger.debug(f"processing line '{line.strip()}'")
        prefix, config_str = line.split(":")
        configs = [_.strip() for _ in config_str.split(";")]

        game_match = game_regex.fullmatch(prefix)
        assert game_match is not None

        game_id = int(game_match[1])
        logger.debug(f"{game_id=}")

        possible = True
        for config in configs:
            logger.debug(f"{config=}")
            color_specs = [_.strip() for _ in config.split(",")]
            counts = {"red": 0, "green": 0, "blue": 0}
            for spec in color_specs:
                logger.debug(f"color {spec=}")
                match = color_regex.fullmatch(spec)
                count = int(match[1])
                color = match[2]
                assert counts[color] == 0

                logger.debug(f"{count=} of {color=}")
                counts[color] = count

            for key, value in counts.items():
                if value > MAX_COUNTS[key]:
                    logger.debug(f"too many {key} balls")
                    possible = False
                    break

            if not possible:
                break

        if possible:
            logger.debug(f"game {game_id} is possible")
            id_sum += game_id
        else:
            logger.debug(f"game {game_id} is impossible")

    print(f"Sum of IDs of possible games is {id_sum}.")
