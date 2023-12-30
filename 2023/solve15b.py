#! /usr/bin/env python
from collections import defaultdict

from utils import logger

from common15 import HASH, read_steps


if __name__ == "__main__":
    steps = read_steps()

    # kinda cheating to use dict
    boxes = defaultdict(dict)
    for step in steps:
        if "-" in step:
            assert step.endswith("-")
            key = step[:-1]
            value = None
        elif "=" in step:
            key, value = step.split("=")
            value = int(value)
        else:
            raise ValueError(f"Invalid {step=}")

        h = HASH(key)
        box_contents = boxes[h]
        if value is None:
            box_contents.pop(key, None)
        else:
            box_contents[key] = value

    logger.debug(f"Final box contents:")
    for box_id in sorted(boxes.keys()):
        box_contents = boxes[box_id]
        if len(box_contents) > 0:
            box_str = " ".join(
                f"[{key} {value}]" for key, value in box_contents.items()
            )
            logger.debug(f"Box {box_id}: {box_str}")

    power = 0
    for box_id, box in boxes.items():
        for i, (lens, focal_length) in enumerate(box.items()):
            lens_power = (1 + box_id) * (i + 1) * focal_length
            logger.debug(f"power of {lens}: {lens_power}")
            power += lens_power

    print(f"Focusing power of resulting lens configuration: {power}")
