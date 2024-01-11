#! /usr/bin/env python
import re
from utils import iterinput, logger

from common18 import area_inside


if __name__ == "__main__":
    regex = re.compile(r"([RDLU])\s+(\d+)\s+\(#([0-9a-fA-F]+)\)")
    instructions = []
    for line in iterinput():
        match = regex.fullmatch(line)
        assert match is not None

        _, _, hex = match.groups()
        instructions.append(hex)

    logger.debug(f"{instructions=}")

    dig_plan = []
    for instruction in instructions:
        dir = "RDLU"[int(instruction[-1])]
        count = int(instruction[:-1], 16)
        dig_plan.append((dir, count))

    logger.debug(f"{dig_plan=}")

    area = area_inside(dig_plan)
    print(f"The lagoon would hold {area} cubic meters of lava")
